from fastapi import BackgroundTasks
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from models.Message import Message
from models.ChatMessage import ChatMessage, ChatMessages
from services.abstraction.ILLMService import ILLMService
from services.abstraction.ILoggerService import ILoggerService
from tools.abstraction.IToolFactory import IToolFactory
from langchain.schema import SystemMessage

class LLMService(ILLMService):
  def __init__(self, rabbitmq_client: IRabbitMqClient, logger: ILoggerService, tool_factory: IToolFactory):
    self.tool_factory = tool_factory
    self.tools = self.tool_factory.create_tools()
    self.rabbitmq_client = rabbitmq_client
    self.logger = logger
    self.llm = init_chat_model("openai:gpt-4.1")
    
    prompt = SystemMessage(
      content="""
      You are a helpful financial assistant in a finance application.
      Use the following tools to assist with financial queries.
      Always think step-by-step and use the tools when necessary.
      If you don't know the answer, just say you don't know. Do not make up an answer.
      If information is missing, make the best assumption and proceed.
      I always send the user_id and correlation_id in system message. These are only for internal use never to be shared with the user.
      Return your response as a single-line string. Do not include any newline characters (\n) or line breaks.
      Never ask the user for clarification."""
    )

    self.agent = create_react_agent(
      model=self.llm,
      tools=self.tools,
      prompt=prompt
    )

  async def process_and_publish_prompt(
      self, prompt: str, 
      correlation_id: str, 
      exchange: str, 
      user_id: str = None, 
      routing_key: str = None
    ):

    try:
      message = ChatMessages(
        messages=[
          ChatMessage(role="system", content="user_id: " + user_id + " correlation_id: " + correlation_id),
          ChatMessage(role="user", content=prompt)
        ]
      )

      message_dump = message.model_dump()
      response = await self.agent.ainvoke(message_dump)
      messages = response.get('messages', [])
      last_message = messages[-1]
      result = getattr(last_message, 'content', '')

      message = Message(
        CorrelationId=correlation_id,
        Success=True,
        UserId=user_id,
        Prompt=prompt,
        Response=result
      )

      message_json = message.model_dump()
      await self.rabbitmq_client.publish_async(exchange, routing_key, message_json)
      self.logger.info(f"Successfully processed LLM request {correlation_id}")

    except Exception as e:
      error_message = Message(
        CorrelationId=correlation_id,
        Success=False,
        UserId=user_id,
        Prompt=prompt,
        Error=str(e)
      )
      
      await self.rabbitmq_client.publish_async(exchange, routing_key, error_message)
      self.logger.error(f"Error processing LLM request {correlation_id}: {str(e)}")

  async def send_prompt_sync_process(self, prompt: str, user_id: str, correlation_id: str) -> str:
    try:
      messages = ChatMessages(
        messages=[
          ChatMessage(role="system", content="user_id: " + user_id + " correlation_id: " + correlation_id),
          ChatMessage(role="user", content=prompt)
        ]
      )
      message_dump = messages.model_dump()
      result = await self.agent.ainvoke(message_dump)

    except Exception as e:
      self.logger.error(f"Error during ainvoke: {e}")
      result = None

    self.logger.info(f"Successfully processed LLM request {correlation_id}")
    return result

  def send_prompt_async_process(
    self,
    prompt: str,
    user_id: str,
    correlation_id: str, 
    routing_key: str, 
    exchange: str, 
    background_tasks: BackgroundTasks
  ):
    try:
      background_tasks.add_task(
        self.process_and_publish_prompt,
        prompt,
        correlation_id,
        exchange,
        user_id,
        routing_key,
      )
      self.logger.info(f"Successfully scheduled LLM request {correlation_id}")
      return {"Status": "success", "CorrelationId": correlation_id, "Message": "Request received and will be processed"}

    except Exception as e:
      self.logger.error(f"Error scheduling LLM request {correlation_id}: {str(e)}")
      return {"Status": "error", "Message": str(e)}