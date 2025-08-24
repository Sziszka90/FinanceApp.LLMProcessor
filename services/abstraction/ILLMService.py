from abc import ABC, abstractmethod
from typing import List

class ILLMService(ABC):
  @abstractmethod
  async def get_llm_response(self, prompt: str) -> str:
    pass

  @abstractmethod
  async def get_llm_response_with_tools(self, prompt: str, user_id: str) -> str:
    pass

  @abstractmethod
  def get_matched_transactions_prompt(self, transaction_names: List[str], transaction_group_names: List[str]) -> str:
    pass
