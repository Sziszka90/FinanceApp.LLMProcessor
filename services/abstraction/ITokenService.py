from abc import ABC, abstractmethod
from email.header import Header

class ITokenService(ABC):
	@abstractmethod
	def validate_token(self, authorization: str = Header(...)) -> bool:
		pass
