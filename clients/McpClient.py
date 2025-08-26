
import httpx
from clients.abstraction.IMcpClient import IMcpClient
from models import McpEnvelope
from models.McpRequest import McpRequest

class McpClient(IMcpClient):
  def __init__(self, base_url: str):
    self.base_url = base_url

  async def call_mcp(self, mcp_request: McpRequest) -> McpEnvelope:
    url = "/mcp"
    async with httpx.AsyncClient() as client:
      response = await client.post(f"{self.base_url}{url}", json=mcp_request)
      response.raise_for_status()
      response_data = response.json()
    return McpEnvelope(**response_data)