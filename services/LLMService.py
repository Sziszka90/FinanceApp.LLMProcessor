from fastapi import BackgroundTasks
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from clients.RabbitMqClient import RabbitMqClient
from langchain_core.tools import StructuredTool
from services.LoggerService import LoggerService
from services.abstraction.ILLMService import ILLMService

class LLMService(ILLMService):
  def __init__(self, rabbitmq_client: RabbitMqClient, mcp_dispatcher_tool: StructuredTool, logger: LoggerService):
    self.mcp_dispatcher_tool = mcp_dispatcher_tool
    self.rabbitmq_client = rabbitmq_client
    self.logger = logger
    self.llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    prompt = PromptTemplate.from_template(
      """You must strictly follow the provided tool schema.
        Use only exact parameter names: action, parameters, startDate, endDate, top, userId, correlationId.
        Do not rename or add alternative names. Do not add extra keys.
        Return valid JSON only."""
    )

    self.agent = initialize_agent(
      tools=[self.mcp_dispatcher_tool],
      llm=self.llm,
      agent_type=AgentType.OPENAI_FUNCTIONS,
      handle_parsing_errors=True,
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
      response = await self.agent.ainvoke({"input": prompt})
      message = {
        "correlation_id": correlation_id,
        "success": True,
        "user_id": user_id,
        "prompt": prompt,
        "response": response
      }
      await self.rabbitmq_client.publish_async(exchange, routing_key, message)
      self.logger.info(f"Successfully processed LLM request {correlation_id}")

    except Exception as e:
      error_message = {
        "correlation_id": correlation_id,
        "success": False,
        "user_id": user_id,
        "prompt": prompt,
        "error": str(e)
      }
      await self.rabbitmq_client.publish_async(exchange, routing_key, error_message)
      self.logger.error(f"Error processing LLM request {correlation_id}: {str(e)}")

  async def send_prompt_sync(self, prompt: str, user_id: str, correlation_id: str) -> str:
    try:
      result = await self.agent.ainvoke({
        "input": prompt + " user_id: " + user_id + " correlation_id: " + correlation_id,
      })
    except Exception as e:
      self.logger.error(f"Error during ainvoke: {e}")
      result = None

    self.logger.info(f"Successfully processed LLM request {correlation_id}")
    return result

  def send_prompt_async(
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
        self.execute_prompt_request,
        prompt,
        correlation_id,
        exchange,
        user_id,
        routing_key,
      )
      self.logger.info(f"Successfully scheduled LLM request {correlation_id}")
      return {"status": "success", "correlation_id": correlation_id, "message": "Request received and will be processed"}
    
    except Exception as e:
      self.logger.error(f"Error scheduling LLM request {correlation_id}: {str(e)}")
      return {"status": "error", "message": str(e)}