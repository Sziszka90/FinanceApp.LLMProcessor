import json
import httpx
from clients.abstraction.IMcpClient import IMcpClient
from models.McpEnvelope import McpEnvelope
from models.McpRequest import McpRequest
from services.abstraction.ILoggerService import ILoggerService

class McpClient(IMcpClient):
  def __init__(self, base_url: str, logger: ILoggerService):
    self.base_url = base_url
    self.logger = logger

  async def call_mcp(self, mcp_request: McpRequest) -> McpEnvelope:
    url = "/mcp"
    try:
      async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(f"{self.base_url}{url}", json=mcp_request.model_dump())
        response.raise_for_status()
        response_data = response.json()
        if 'payload' in response_data and not isinstance(response_data['payload'], str):
          response_data['payload'] = json.dumps(response_data['payload'])
        return McpEnvelope(**response_data)
    except Exception as e:
      self.logger.error(f"Error calling MCP: {e}")
      return None