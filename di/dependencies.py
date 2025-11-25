from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from clients.RabbitMqClient import RabbitMqClient
from clients.McpClient import McpClient
from clients.abstraction.IMcpClient import IMcpClient
from database.connection import get_db
from repositories.MatchTransactionRepository import MatchTransactionRepository
from repositories.abstraction.IMatchTransactionRepository import IMatchTransactionRepository
from services.LLMService import LLMService
from services.LoggerService import LoggerService
from services.PromptService import PromptService
from services.TokenService import TokenService
from services.abstraction.ILLMService import ILLMService
from services.abstraction.ILoggerService import ILoggerService
from services.abstraction.IPromptService import IPromptService
from services.abstraction.ITokenService import ITokenService
from tools.McpTool import McpTool
from tools.ToolFactory import ToolFactory
from tools.abstraction.IMcpTool import IMcpTool
from tools.abstraction.IToolFactory import IToolFactory

# Singleton instances (created once, cached)
_rabbitmq_client: IRabbitMqClient = None
_mcp_client: IMcpClient = None
_mcp_tool: IMcpTool = None
_tool_factory: IToolFactory = None

# Singleton services (shared across all requests)
def get_rabbitmq_client() -> IRabbitMqClient:
  """Singleton - RabbitMQ client is shared across requests"""
  global _rabbitmq_client
  if _rabbitmq_client is None:
    logger = LoggerService()
    _rabbitmq_client = RabbitMqClient(logger=logger)
  return _rabbitmq_client

def get_mcp_client() -> IMcpClient:
  """Singleton - MCP client is shared across requests"""
  global _mcp_client
  if _mcp_client is None:
    logger = LoggerService()
    _mcp_client = McpClient(logger=logger)
  return _mcp_client

def get_mcp_tool(mcp_client: IMcpClient = Depends(get_mcp_client)) -> IMcpTool:
  """Singleton - MCP tool is shared across requests"""
  global _mcp_tool
  if _mcp_tool is None:
    logger = LoggerService()
    _mcp_tool = McpTool(mcp_client, logger=logger)
  return _mcp_tool

def get_tool_factory(mcp_tool: IMcpTool = Depends(get_mcp_tool)) -> IToolFactory:
  """Singleton - ToolFactory is shared across requests"""
  global _tool_factory
  if _tool_factory is None:
    _tool_factory = ToolFactory(mcp_tool)
  return _tool_factory

# Request-scoped services (new instance per request)
def get_logger_service() -> ILoggerService:
  """Request-scoped - new logger instance per request"""
  return LoggerService()

def get_prompt_service() -> IPromptService:
  """Request-scoped - new prompt service instance per request"""
  return PromptService()

def get_token_service(logger: ILoggerService = Depends(get_logger_service)) -> ITokenService:
  """Request-scoped - new token service instance per request"""
  return TokenService(logger=logger)

def authorize_token(authorization: str = Header(...), token_service: ITokenService = Depends(get_token_service)):
  """Validates authorization token using request-scoped token service"""
  token_service.validate_token(authorization)
  return authorization

def get_match_transaction_repository(
  db: AsyncSession = Depends(get_db),
  logger: ILoggerService = Depends(get_logger_service)
) -> IMatchTransactionRepository:
  """Request-scoped repository with request-scoped async DB session and logger"""
  return MatchTransactionRepository(db, logger)

def get_llm_service(
  rabbitmq_client: IRabbitMqClient = Depends(get_rabbitmq_client),
  tool_factory: IToolFactory = Depends(get_tool_factory),
  logger: ILoggerService = Depends(get_logger_service),
  prompt_service: IPromptService = Depends(get_prompt_service),
  matchTransactionRepository: IMatchTransactionRepository = Depends(get_match_transaction_repository)
) -> ILLMService:
  """Request-scoped - new LLM service instance per request with scoped dependencies"""
  return LLMService(
    rabbitmq_client=rabbitmq_client,
    tool_factory=tool_factory,
    logger=logger,
    prompt_service=prompt_service,
    matchTransactionRepository=matchTransactionRepository
  )
