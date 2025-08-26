
from injector import Injector
from langchain_core.tools import StructuredTool
import asyncio
from clients.McpClient import McpClient
from modules.AppModule import AppModule

injector = Injector([AppModule()])
mcp_client = injector.get(McpClient)

def mcp_tool(mcp_client: McpClient):
  return asyncio.run(mcp_client.call_mcp())

mcp_dispatcher_tool = StructuredTool.from_function(
  func=mcp_tool,
  name="mcp_tool",
  description="Call backend MCP service to perform financial operations such as fetching transaction groups, spending, etc. Specify the tool name and arguments."
)
