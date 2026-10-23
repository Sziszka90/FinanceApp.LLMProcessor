from abc import ABC, abstractmethod

class IPromptService(ABC):
  @abstractmethod
  def get_matched_transactions_prompt(
    self,
    transaction_names: list[str],
    transaction_group_names: list[str],
  ) -> str:
    """
    Get a prompt for matching transactions.
    """
    pass

  @abstractmethod
  def get_pdf_import_system_prompt(self) -> str:
    """Return the instructions for extracting transactions from a bank statement."""
    pass

  @abstractmethod
  def get_pdf_import_user_prompt(self, custom_prompt: str | None = None) -> str:
    """Return the user instruction for extracting a PDF bank statement."""
    pass
