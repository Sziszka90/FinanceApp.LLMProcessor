from fastapi import BackgroundTasks
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from clients.RabbitMqClient import RabbitMqClient
from tools.tools import mcp_dispatcher_tool

class LLMService:
  def __init__(self, rabbitmq_client: RabbitMqClient):
    self.llm = ChatOpenAI(model="GPT-4", temperature=0)
    self.agent = initialize_agent(
      tools=[mcp_dispatcher_tool],
      llm=self.llm,
      agent_type=AgentType.OPENAI_FUNCTIONS
    )
    self.rabbitmq_client = rabbitmq_client

  async def send_prompt_sync(self, query: str):
    await self.agent.arun(query)
  
  async def handle_prompt_async(self, prompt: str, correlation_id: str, exchange: str, user_id: str = None, routing_key: str = None):
    try:
      response = await self.send_prompt_sync(prompt)
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
        self.handle_prompt_async,
        prompt,
        correlation_id,
        exchange,
        user_id,
        routing_key,
      )
      return {"status": "success", "correlation_id": correlation_id, "message": "Request received and will be processed"}
    
    except Exception as e:
      return {"status": "error", "message": str(e)}