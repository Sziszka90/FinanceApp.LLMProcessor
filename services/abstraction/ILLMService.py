from abc import ABC, abstractmethod

class ILLMService(ABC):
	@abstractmethod
	async def send_prompt_async(self, prompt: str, correlation_id: str, exchange: str, user_id: str = None, routing_key: str = None):
		"""
		Send a prompt to the LLM asynchronously via RabbitMQ.
		"""
		pass

	@abstractmethod
	def send_prompt_sync(self, prompt: str) -> str:
		"""
		Send a prompt to the LLM synchronously via REST.
		"""
		pass
