from abc import ABC, abstractmethod

class ILLMService(ABC):
	@abstractmethod
	async def send_prompt_async(self, prompt: str, correlation_id: str, exchange: str, user_id: str = None, routing_key: str = None):
		pass

	@abstractmethod
	def send_prompt_sync(self, prompt: str) -> str:
		pass
