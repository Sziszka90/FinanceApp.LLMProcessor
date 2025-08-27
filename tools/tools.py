
from langchain_core.tools import StructuredTool

def create_mcp_dispatcher_tool(mcp_tool_runner):
  return StructuredTool.from_function(
    func=mcp_tool_runner,
    name="mcp_tool",
    description="Call backend MCP service to perform financial operations such as fetching transaction groups, spending, etc. Specify the tool name and arguments."
  )
