import json
from tools import McpTool

def create_mcp_tool_runner(mcp_tool: McpTool):
  async def run_mcp_tool(json_input: str) -> str:
    data = json.loads(json_input)
    missing = []
    if "action" not in data:
      missing.append("action")
    if "parameters" not in data:
      missing.append("parameters")
    if missing:
      return f"Error: Missing required input(s): {', '.join(missing)}. Please provide all required fields."
    return await mcp_tool.run(data)
  return run_mcp_tool