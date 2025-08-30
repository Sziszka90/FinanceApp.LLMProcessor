import os
from fastapi import HTTPException, status
from fastapi.params import Header
from services.abstraction.ILoggerService import ILoggerService
from services.abstraction.ITokenService import ITokenService

class TokenService(ITokenService):
  def __init__(self, logger: ILoggerService):
    self.api_token = os.getenv("API_TOKEN")
    self.logger = logger

  def validate_token(self, authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
      self.logger.error("Invalid authorization header")
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    if token != self.api_token:
      self.logger.error("Invalid token")
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    self.logger.info("Token validated successfully")
