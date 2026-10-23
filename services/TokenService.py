import secrets
from fastapi import HTTPException, status
from fastapi.params import Header
from services.abstraction.ILoggerService import ILoggerService
from services.abstraction.ITokenService import ITokenService
from config.settings import get_settings

class TokenService(ITokenService):
  def __init__(self, logger: ILoggerService):
    settings = get_settings()
    self.api_token = settings.api_token
    self.logger = logger

  def validate_token(self, authorization: str = Header(...)) -> bool:
    scheme, separator, token = authorization.partition(" ")
    if scheme.casefold() != "bearer" or not separator or not token.strip():
      self.logger.error("Invalid authorization header")
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    if not self.api_token or not secrets.compare_digest(
      token.strip().encode("utf-8"), self.api_token.encode("utf-8")
    ):
      self.logger.error("Invalid token")
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    self.logger.info("Token validated successfully")
    return True
