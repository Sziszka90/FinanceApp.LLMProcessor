
import httpx
from clients.abstraction.IApiClient import IApiClient
from models.TopTransactionGroupDto import TopTransactionGroupDto

class ApiClient(IApiClient):
  def __init__(self, base_url: str):
    self.base_url = base_url

  async def get(self, url: str, params: dict = None) -> dict:
    async with httpx.AsyncClient() as client:
      response = await client.get(f"{self.base_url}{url}", params=params)
      response.raise_for_status()
      return response.json()

  async def get_top_transaction_group(self, user_id: str, start_date: str, end_date: str, top: int = 10) -> list[TopTransactionGroupDto]:
    url = "/transactiongroups/top"
    params = {
      "user_id": user_id,
      "start_date": start_date,
      "end_date": end_date,
      "top": top
    }
    response_data = await self.get(url, params=params)

    return [TopTransactionGroupDto(**item) for item in response_data]
