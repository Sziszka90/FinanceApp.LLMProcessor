import os

from fastapi import BackgroundTasks
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain.agents import create_agent as langchain_create_agent
from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from models.Message import Message
from models.ChatMessage import ChatMessage, ChatMessages
from repositories.abstraction.IMatchTransactionRepository import IMatchTransactionRepository
from services.abstraction.ILLMService import ILLMService
from services.abstraction.ILoggerService import ILoggerService
from services.abstraction.IPromptService import IPromptService
from tools.abstraction.IToolFactory import IToolFactory
from models.MatchTransactionResponse import MatchTransactionResponse

class LLMService(ILLMService):
  def __init__(
      self, 
      rabbitmq_client: IRabbitMqClient, 
      logger: ILoggerService, 
      tool_factory: IToolFactory,
      prompt_service: IPromptService,
      matchTransactionRepository: IMatchTransactionRepository):
    self.tool_factory = tool_factory
    self.tools = self.tool_factory.create_tools()
    self.rabbitmq_client = rabbitmq_client
    self.logger = logger
    self.prompt_service = prompt_service
    self.matchTransactionRepository = matchTransactionRepository
    self.llm = self._create_llm()

  def _create_llm(self):
    azure_environment = {
      "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
      "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
      "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
    }
    missing_settings = [
      name for name, value in azure_environment.items() if not value
    ]
    if missing_settings:
      raise ValueError(
        "Azure OpenAI configuration is required. Missing: "
        + ", ".join(missing_settings)
      )

    api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
      raise ValueError(
        "Azure OpenAI requires AZURE_OPENAI_API_KEY or OPENAI_API_KEY"
      )

    endpoint = azure_environment["AZURE_OPENAI_ENDPOINT"].rstrip("/")

    return ChatOpenAI(
      base_url=endpoint,
      api_key=api_key,
      model=azure_environment["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )


  async def match_transactions(
      self, 
      correlation_id: str, 
      exchange: str, 
      transaction_names: list[str],
      transaction_group_names: list[str],
      user_id: str = None, 
      routing_key: str = None
    ):

    matching_prompt = self.prompt_service.get_matched_transactions_prompt(
      transaction_names, 
      transaction_group_names
    )

    matching_agent = langchain_create_agent(
      model=self.llm,
      tools=[],
      system_prompt=matching_prompt
    )

    message = ChatMessages(
      messages=[
        ChatMessage(role="system", content="user_id: " + user_id + " correlation_id: " + correlation_id),
      ]
    )

    try:
      message_dump = message.model_dump()
      response = await matching_agent.ainvoke(message_dump)
      messages = response.get('messages', [])
      last_message = messages[-1]
      result = getattr(last_message, 'content', '')
    
      try:
        match_response = MatchTransactionResponse.model_validate_json(result)
        
        if match_response and match_response.transactions:
          try:
            await self.matchTransactionRepository.save_match_transactions(
              match_response.transactions,
              correlation_id
            )
            self.logger.info(f"Saved {len(match_response.transactions)} transaction matches to database")
          except Exception as db_error:
            self.logger.error(f"Error saving matches to database: {db_error}")
            
      except Exception as e:
        self.logger.error(f"Error parsing MatchTransactionResponse: {e}")

      message = Message[MatchTransactionResponse](
        correlation_id=correlation_id,
        success=True,
        user_id=user_id,
        prompt=matching_prompt,
      )

      message_json = message.model_dump()
      await self.rabbitmq_client.publish_async(exchange, routing_key, message_json)
      self.logger.info(f"Successfully processed LLM request {correlation_id}")

    except Exception as e:
      error_message = Message[str](
        correlation_id=correlation_id,
        success=False,
        user_id=user_id,
        prompt=matching_prompt,
        error=str(e)
      )
      
      await self.rabbitmq_client.publish_async(exchange, routing_key, error_message)
      self.logger.error(f"Error processing LLM request {correlation_id}: {str(e)}")

  async def send_prompt(self, prompt: str, user_id: str, correlation_id: str) -> str:
    try:
      mcp_prompt = self.prompt_service.get_mcp_prompt()

      mcp_agent = langchain_create_agent(
        model=self.llm,
        tools=self.tools,
        system_prompt=mcp_prompt
      )

      messages = ChatMessages(
        messages=[
          ChatMessage(role="system", content="user_id: " + user_id + " correlation_id: " + correlation_id),
          ChatMessage(role="user", content=prompt)
        ]
      )
      message_dump = messages.model_dump()

      result = await mcp_agent.ainvoke(message_dump)

    except Exception as e:
      self.logger.error(f"Error during ainvoke: {e}")
      result = None

    self.logger.info(f"Successfully processed LLM request {correlation_id}")
    return result

  def match_transactions_async(
    self,
    transactions: list[str],
    transaction_groups: list[str],
    user_id: str,
    correlation_id: str, 
    routing_key: str, 
    exchange: str, 
    background_tasks: BackgroundTasks
  ):
    try:
      background_tasks.add_task(
        self.match_transactions,
        correlation_id,
        exchange,
        transactions,
        transaction_groups,
        user_id,
        routing_key,
      )
      self.logger.info(f"Successfully scheduled LLM request {correlation_id}")
      return {"Status": "success", "CorrelationId": correlation_id, "Message": "Request received and will be processed"}

    except Exception as e:
      self.logger.error(f"Error scheduling LLM request {correlation_id}: {str(e)}")
      return {"Status": "error", "Message": str(e)}