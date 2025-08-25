import asyncio
from fastapi import Header, HTTPException, status
from clients.ApiClient import ApiClient
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

def get_top_transaction_groups_sync(user_id: str, start_date: str, end_date: str, top: int = 10):
  api_client = injector.get(ApiClient)
  return asyncio.run(api_client.get_top_transaction_group(user_id, start_date, end_date, top))
