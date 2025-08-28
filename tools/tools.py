from langchain_core.tools import StructuredTool

from models.McpToolRequest import MCPToolRequest

def create_structured_tool(mcp_tool_runner):
  return StructuredTool.from_function(
    func=mcp_tool_runner,
    name="mcp_tool",
    args_schema=MCPToolRequest,
    description="Call backend MCP service to perform financial operations. Query data from backend related to user, transactions, transaction groups. Use only the parameter names defined in the schema.",
    coroutine=mcp_tool_runner,
  )