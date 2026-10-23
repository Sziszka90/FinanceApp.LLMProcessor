from clients.McpClient import McpClient
from models.McpRequest import McpRequest
from services.abstraction.ILoggerService import ILoggerService
from tools.abstraction.IMcpTool import IMcpTool

class McpTool(IMcpTool):
  def __init__(self, mcp_client: McpClient, logger: ILoggerService):
    self.mcp_client = mcp_client
    self.logger = logger

  async def run(self, mcp_request: McpRequest):
    self.logger.info("Running MCP tool %s", mcp_request.tool_name)
    response = await self.mcp_client.call_mcp(mcp_request)
    self.logger.info("MCP tool %s completed", mcp_request.tool_name)
    return response
