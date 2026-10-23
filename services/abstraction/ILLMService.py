from abc import ABC, abstractmethod
class ILLMService(ABC):
	@abstractmethod
	async def match_transactions(
		self, 
		correlation_id: str, 
		transaction_names: list[str],
		transaction_group_names: list[str],
		user_id: str,
	) -> None:
		"""
		Match transactions to groups and publish the mapping to RabbitMQ.
		"""
		pass
