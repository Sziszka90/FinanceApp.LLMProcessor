import httpx
from clients.abstraction.IMcpClient import IMcpClient
from models import McpEnvelope
from models.McpRequest import McpRequest
from services.LoggerService import LoggerService

class McpClient(IMcpClient):
  def __init__(self, base_url: str, logger: LoggerService):
    self.base_url = base_url
    self.logger = logger

  async def call_mcp(self, mcp_request: McpRequest) -> McpEnvelope:
    url = "/mcp"
    try:
      async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(f"{self.base_url}{url}", json=mcp_request)
        response.raise_for_status()
        response_data = response.json()
      return McpEnvelope(**response_data)
    except Exception as e:
      self.logger.error(f"Error calling MCP: {e}")
      return None