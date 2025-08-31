import json
import os
import httpx
from clients.abstraction.IMcpClient import IMcpClient
from models.McpEnvelope import McpEnvelope
from models.McpRequest import McpRequest
from services.abstraction.ILoggerService import ILoggerService

class McpClient(IMcpClient):
  def __init__(self, logger: ILoggerService):
    self.logger = logger

  async def call_mcp(self, mcp_request: McpRequest) -> McpEnvelope:
    url = os.getenv("MCP_API_BASE_URL")
    if not url:
      raise ValueError("MCP_API_BASE_URL not set")
    try:
      async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(url, json=mcp_request.model_dump())
        response.raise_for_status()
        response_data = response.json()
        if 'Payload' in response_data and not isinstance(response_data['Payload'], str):
          response_data['Payload'] = json.dumps(response_data['Payload'])
        return McpEnvelope(**response_data)
    except Exception as e:
      self.logger.error(f"Error calling MCP: {e}")
      return None