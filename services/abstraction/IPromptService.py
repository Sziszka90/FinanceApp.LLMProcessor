from abc import ABC, abstractmethod

class IPromptService(ABC):
  @abstractmethod
  def get_matched_transactions_prompt(self, transaction_names: list[str], transaction_group_names: list[str]) -> str:
    """
    Get a prompt for matching transactions.
    """
    pass