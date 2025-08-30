import os
from injector import Binder, Module, provider, singleton
from clients.McpClient import McpClient
from clients.abstraction.IMcpClient import IMcpClient
from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from services.LLMService import LLMService
from services.LoggerService import LoggerService
from services.PromptService import PromptService
from services.TokenService import TokenService
from clients.RabbitMqClient import RabbitMqClient
from services.abstraction.ILLMService import ILLMService
from services.abstraction.ILoggerService import ILoggerService
from services.abstraction.IPromptService import IPromptService
from services.abstraction.ITokenService import ITokenService
from tools.McpTool import McpTool
from tools.ToolFactory import ToolFactory
from tools.abstraction.IMcpTool import IMcpTool
from tools.abstraction.IToolFactory import IToolFactory

class AppModule(Module):
  def configure(self, binder: Binder):
    binder.bind(ILoggerService, to=self.create_logger_service, scope=singleton)
    binder.bind(IMcpClient, to=self.create_mcp_client, scope=singleton)
    binder.bind(IMcpTool, to=self.create_mcp_tool, scope=singleton)
    binder.bind(IRabbitMqClient, to=self.create_rabbitmq_client, scope=singleton)
    binder.bind(IToolFactory, to=self.create_tool_factory, scope=singleton)
    binder.bind(ILLMService, to=self.create_llm_service, scope=singleton)
    binder.bind(IPromptService, to=self.create_prompt_service, scope=singleton)
    binder.bind(ITokenService, to=self.create_token_service, scope=singleton)

  @singleton
  @provider
  def create_logger_service(self) -> ILoggerService:
    return LoggerService()

  @singleton
  @provider
  def create_mcp_client(self, logger: ILoggerService) -> IMcpClient:
    return McpClient(logger=logger)

  @singleton
  @provider
  def create_mcp_tool(self, mcp_client: IMcpClient, logger: ILoggerService) -> IMcpTool:
    return McpTool(mcp_client, logger=logger)

  @singleton
  @provider
  def create_rabbitmq_client(self, logger: ILoggerService) -> IRabbitMqClient:
    return RabbitMqClient(logger=logger)

  @singleton
  @provider
  def create_tool_factory(self, mcp_tool: IMcpTool) -> IToolFactory:
    return ToolFactory(mcp_tool)

  @singleton
  @provider
  def create_llm_service(self, rabbitmq_client: IRabbitMqClient, tool_factory: IToolFactory, logger: ILoggerService) -> ILLMService:
    return LLMService(rabbitmq_client=rabbitmq_client, tool_factory=tool_factory, logger=logger)

  @singleton
  @provider
  def create_prompt_service(self) -> IPromptService:
    return PromptService()

  @singleton
  @provider
  def create_token_service(self, logger: ILoggerService) -> ITokenService:
    return TokenService(logger=logger)


