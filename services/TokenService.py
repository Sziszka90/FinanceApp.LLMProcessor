import os
from fastapi import HTTPException, status
from fastapi.params import Header
from services.abstraction.ITokenService import ITokenService

class TokenService(ITokenService):
  def __init__(self):
    self.api_token = os.getenv("API_TOKEN")

  def validate_token(self, authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    if token != self.api_token:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
