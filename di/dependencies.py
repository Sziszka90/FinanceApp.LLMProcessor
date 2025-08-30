from fastapi import Header
from injector import Injector
from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from di.AppModule import AppModule
from services.abstraction.ILLMService import ILLMService
from services.abstraction.IPromptService import IPromptService
from services.abstraction.ITokenService import ITokenService

injector = Injector([AppModule()])

def get_rabbitmq_client() -> IRabbitMqClient:
  return injector.get(IRabbitMqClient)

def authorize_token(authorization: str = Header(...)):
  token_service = injector.get(ITokenService)
  token_service.validate_token(authorization)
  return authorization

def get_llm_service() -> ILLMService:
  return injector.get(ILLMService)

def get_prompt_service() -> IPromptService:
  return injector.get(IPromptService)

