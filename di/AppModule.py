import os
from injector import Module, provider, singleton
from clients import McpClient
from services import LLMService, PromptService
from clients.RabbitMqClient import RabbitMqClient

class AppModule(Module):
  @singleton
  @provider
  def get_mcp_client(self) -> McpClient:
    return McpClient(mcp_url=os.getenv("API_URL"))

  @singleton
  @provider
  def get_llm_service(self, rabbitmq_client: RabbitMqClient) -> LLMService:
    return LLMService(api_key=os.getenv("LLM_API_KEY"), rabbitmq_client=rabbitmq_client)

  @singleton
  @provider
  def get_prompt_service(self) -> PromptService:
    return PromptService()

  @singleton
  @provider
  def get_rabbitmq_client(self) -> RabbitMqClient:
    return RabbitMqClient()