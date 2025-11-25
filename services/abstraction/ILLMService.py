from abc import ABC, abstractmethod
from fastapi import BackgroundTasks

class ILLMService(ABC):
	@abstractmethod
	async def match_transactions(
		self, 
		correlation_id: str, 
		exchange: str, 
		transaction_names: list[str],
		transaction_group_names: list[str],
		user_id: str = None, 
		routing_key: str = None
	):
		"""
		Match transactions to transaction groups using LLM and save to database.
		Publishes result to RabbitMQ.
		"""
		pass

	@abstractmethod
	async def send_prompt(self, prompt: str, user_id: str, correlation_id: str) -> str:
		"""
		Send a prompt to the LLM synchronously and return the result.
		Uses MCP tools for enhanced capabilities.
		"""
		pass

	@abstractmethod
	def match_transactions_async(
		self,
		transactions: list[str],
		transaction_groups: list[str],
		user_id: str,
		correlation_id: str, 
		routing_key: str, 
		exchange: str, 
		background_tasks: BackgroundTasks
	):
		"""
		Schedule transaction matching as a background task.
		Returns immediately with a success/error status.
		"""
		pass
