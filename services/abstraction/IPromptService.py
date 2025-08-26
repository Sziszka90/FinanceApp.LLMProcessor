from abc import ABC, abstractmethod
from typing import List

class IPromptService(ABC):
  @abstractmethod
  def get_matched_transactions_prompt(self, transaction_names: List[str], transaction_group_names: List[str]) -> str:
    pass