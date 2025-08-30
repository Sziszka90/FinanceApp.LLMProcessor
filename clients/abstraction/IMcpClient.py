from abc import ABC, abstractmethod
from models.McpEnvelope import McpEnvelope
from models.McpRequest import McpRequest

class IMcpClient(ABC):
  @abstractmethod
  async def call_mcp(self, mcp_request: McpRequest) -> McpEnvelope:
    """
    Calls the backend MCP service with the given request and returns the response envelope.
    """
    pass
