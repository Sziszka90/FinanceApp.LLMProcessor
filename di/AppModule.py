import os
from injector import Module, provider, singleton
from clients import McpClient
from clients.ApiClient import ApiClient
from services import LLMService

class AppModule(Module):
  @singleton
  @provider
  def get_api_client(self) -> ApiClient:
    return ApiClient(base_url=os.getenv("API_URL"))

  @singleton
  @provider
  def get_mcp_client(self) -> McpClient:
    return McpClient(mcp_url=os.getenv("API_URL"))

  @singleton
  @provider
  def get_llm_service(self) -> LLMService:
    return LLMService(api_key=os.getenv("LLM_API_KEY"))