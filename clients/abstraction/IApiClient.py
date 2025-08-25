from abc import ABC, abstractmethod


class IApiClient(ABC):
  @abstractmethod
  async def get_top_transaction_group(self, user_id: str, start_date: str, end_date: str, top: int = 10) -> dict:
    """Send request to backend to get top transaction groups."""
    pass
