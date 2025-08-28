import os
from injector import Binder, Module, provider, singleton
from clients.McpClient import McpClient
from services.LLMService import LLMService
from services.PromptService import PromptService
from services.TokenService import TokenService
from clients.RabbitMqClient import RabbitMqClient
from tools.McpTool import McpTool
from langchain_core.tools import StructuredTool
from tools.tool_runner import create_mcp_tool_runner
from tools.tools import create_structured_tool

class AppModule(Module):
  def configure(self, binder: Binder):
    binder.bind(McpClient, to=self.create_mcp_client, scope=singleton)
    binder.bind(McpTool, to=self.create_mcp_tool, scope=singleton)
    binder.bind(RabbitMqClient, to=self.create_rabbitmq_client, scope=singleton)
    binder.bind(StructuredTool, to=self.create_mcp_dispatcher_tool, scope=singleton)
    binder.bind(LLMService, to=self.create_llm_service, scope=singleton)
    binder.bind(PromptService, to=self.create_prompt_service, scope=singleton)
    binder.bind(TokenService, to=self.create_token_service, scope=singleton)

  @singleton
  @provider
  def create_mcp_client(self) -> McpClient:
    return McpClient(base_url=os.getenv("API_URL"))

  @singleton
  @provider
  def create_mcp_tool(self, mcp_client: McpClient) -> McpTool:
    return McpTool(mcp_client)

  @singleton
  @provider
  def create_rabbitmq_client(self) -> RabbitMqClient:
    return RabbitMqClient()

  @singleton
  @provider
  def create_mcp_dispatcher_tool(self, mcp_tool: McpTool) -> StructuredTool:
    mcp_tool_runner = create_mcp_tool_runner(mcp_tool)
    return create_structured_tool(mcp_tool_runner)

  @singleton
  @provider
  def create_llm_service(self, rabbitmq_client: RabbitMqClient, mcp_dispatcher_tool: StructuredTool) -> LLMService:
    return LLMService(rabbitmq_client=rabbitmq_client, mcp_dispatcher_tool=mcp_dispatcher_tool)

  @singleton
  @provider
  def create_prompt_service(self) -> PromptService:
    return PromptService()

  @singleton
  @provider
  def create_token_service(self) -> TokenService:
    return TokenService()


