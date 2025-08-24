from abc import ABC, abstractmethod

class IFinanceAppApiClient(ABC):
  @abstractmethod
  async def get_top_transaction_groups(
    self,
    start_date: str,
    end_date: str,
    top: int = 10,
    user_id: str = None
  ):
    pass
