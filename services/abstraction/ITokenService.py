from abc import ABC, abstractmethod

class ITokenService(ABC):
  @abstractmethod
  def validate_token(self, authorization: str) -> bool:
    pass
