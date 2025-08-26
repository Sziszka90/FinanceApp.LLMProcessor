from email.header import Header
from fastapi import HTTPException, status
import injector
from modules.AppModule import AppModule
from services import PromptService, TokenService
from services.LLMService import LLMService

injector = injector.Injector([AppModule()])

def authorize_token(authorization: str = Header(...)):
  token_service = injector.get(TokenService)
  if not token_service.validate_token(authorization):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
  return authorization

def get_llm_service() -> LLMService:
  return injector.get(LLMService)

def get_prompt_service() -> PromptService:
  return injector.get(PromptService)
