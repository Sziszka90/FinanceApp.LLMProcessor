from clients.McpClient import McpClient
from tools.abstraction.IMcpTool import IMcpTool

class McpTool(IMcpTool):
  def __init__(self, mcp_client: McpClient):
    self.mcp_client = mcp_client

  async def run(self, *args, **kwargs):
    return await self.mcp_client.call_mcp(*args, **kwargs)
