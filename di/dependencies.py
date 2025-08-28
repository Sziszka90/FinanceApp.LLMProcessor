from fastapi import Header
from injector import Injector
from clients.McpClient import McpClient
from clients.RabbitMqClient import RabbitMqClient
from di.AppModule import AppModule
from services import LoggerService
from services.TokenService import TokenService
from services.LLMService import LLMService
from services.PromptService import PromptService

injector = Injector([AppModule()])

def get_logger_service() -> LoggerService:
  return injector.get(LoggerService)

def get_rabbitmq_client() -> RabbitMqClient:
  return injector.get(RabbitMqClient)

def get_mcp_client() -> McpClient:
  return injector.get(McpClient)

def authorize_token(authorization: str = Header(...)):
  token_service = injector.get(TokenService)
  token_service.validate_token(authorization)
  return authorization

def get_llm_service() -> LLMService:
  return injector.get(LLMService)

def get_prompt_service() -> PromptService:
  return injector.get(PromptService)

