from fastapi import Header, HTTPException, status
from services import LLMService, TokenService
from injector import Injector
from modules import AppModule

injector = Injector([AppModule()])

def authorize_token(authorization: str = Header(...)):
  token_service = injector.get(TokenService)
  if not token_service.validate_token(authorization):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
  return authorization

def get_llm_service() -> LLMService:
  return injector.get(LLMService)