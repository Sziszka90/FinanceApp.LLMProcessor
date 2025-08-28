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
    parameters = data.get("parameters", {})

    if data.get("action") == "get_top_transaction_groups":
      if not parameters.get("startDate"):
        parameters["startDate"] = "2000-01-01T00:00:00Z"
      if not parameters.get("endDate"):
        parameters["endDate"] = "2100-01-31T23:59:59Z"
      if not parameters.get("top"):
        parameters["top"] = 10

    return await mcp_tool.run(data)
  return run_mcp_tool