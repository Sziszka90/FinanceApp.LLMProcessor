from fastapi import BackgroundTasks
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from clients.RabbitMqClient import RabbitMqClient
from langchain_core.tools import StructuredTool
from services.abstraction.ILLMService import ILLMService


class LLMService(ILLMService):
  def __init__(self, rabbitmq_client: RabbitMqClient, mcp_dispatcher_tool: StructuredTool):
    self.mcp_dispatcher_tool = mcp_dispatcher_tool
    self.llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    prompt_template = PromptTemplate(
      input_variables=["input", "user_id", "correlation_id"],
      template="""
      System: You are an assistant that can call tools.
      User ID: {user_id}
      Correlation ID: {correlation_id}

      Task: {input}
      """
    )
    
    self.agent = initialize_agent(
      tools=[self.mcp_dispatcher_tool],
      llm=self.llm,
      agent_type=AgentType.OPENAI_FUNCTIONS,
      handle_parsing_errors=True,
      prompt=prompt_template
    )
    self.rabbitmq_client = rabbitmq_client

  async def execute_prompt_request(self, prompt: str, correlation_id: str, exchange: str, user_id: str = None, routing_key: str = None):
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
    except Exception as e:
      error_message = {
        "correlation_id": correlation_id,
        "success": False,
        "user_id": user_id,
        "prompt": prompt,
        "error": str(e)
      }
      await self.rabbitmq_client.publish_async(exchange, routing_key, error_message)
      print(f"[ERROR] Failed to process LLM request {correlation_id}: {e}")

  async def send_prompt_sync(self, prompt: str, user_id: str, correlation_id: str) -> str:
    result = await self.agent.ainvoke({
    "input": prompt,
    "user_id": user_id,
    "correlation_id": correlation_id
  })
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
      return {"status": "success", "correlation_id": correlation_id, "message": "Request received and will be processed"}
    
    except Exception as e:
      return {"status": "error", "message": str(e)}