import os
from injector import Module, provider, singleton
from clients import McpClient
from services import LLMService, TokenService

class AppModule(Module):
  @singleton
  @provider
  def get_finance_app_api_client(self) -> McpClient:
    return McpClient(base_url=os.getenv("API_URL"), logger_service=None)

  @singleton
  @provider
  def get_llm_service(self, finance_app_api_client: McpClient) -> LLMService:
    return LLMService(
      api_key=os.getenv("LLM_API_KEY"),
      finance_app_api_client=finance_app_api_client,
    )

  @singleton
  @provider
  def get_token_service(self) -> TokenService:
    return TokenService()
