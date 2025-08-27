import json
from tools import McpTool

def create_run_mcp_tool(mcp_tool: McpTool):
  async def run_mcp_tool(json_input: str) -> str:
    data = json.loads(json_input)
    return await mcp_tool.run(
      action=data["action"],
      parameters=data.get("parameters", {})
    )
  return run_mcp_tool