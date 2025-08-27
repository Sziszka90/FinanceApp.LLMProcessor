import os
from injector import Injector, Module, provider, singleton
from clients import McpClient
from services import LLMService, PromptService
from clients.RabbitMqClient import RabbitMqClient
from tools import McpTool
from tools.tool_runner import create_run_mcp_tool
from tools.tools import create_mcp_dispatcher_tool
from langchain_core.tools import StructuredTool

class AppModule(Module):
  @singleton
  @provider
  def get_mcp_client(self) -> McpClient:
    return McpClient(mcp_url=os.getenv("API_URL"))

  @singleton
  @provider
  def get_llm_service(self, rabbitmq_client: RabbitMqClient, mcp_dispatcher_tool) -> LLMService:
    return LLMService(rabbitmq_client=rabbitmq_client, mcp_dispatcher_tool=mcp_dispatcher_tool)

  @singleton
  @provider
  def get_prompt_service(self) -> PromptService:
    return PromptService()

  @singleton
  @provider
  def get_rabbitmq_client(self) -> RabbitMqClient:
    return RabbitMqClient()
  
  @singleton
  @provider
  def get_mcp_tool(self, mcp_client: McpClient) -> McpTool:
    return McpTool(mcp_client)

  @singleton
  @provider
  def get_mcp_dispatcher_tool(self, mcp_tool: McpTool) -> StructuredTool:
    mcp_tool_runner = create_run_mcp_tool(mcp_tool)
    return create_mcp_dispatcher_tool(mcp_tool_runner)
