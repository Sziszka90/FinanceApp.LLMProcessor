from langchain_core.tools import StructuredTool

def create_structured_tool(mcp_tool_runner):
  return StructuredTool.from_function(
    func=mcp_tool_runner, 
    name="mcp_tool",
    parameters={
      "type": "object",
      "properties": {
        "action": {"type": "string"},
        "parameters": {
          "type": "object",
          "properties": {
            "input": {"type": "string"},
            "user_id": {"type": "string"},
            "correlation_id": {"type": "string"},
          },
          "required": ["input", "user_id", "correlation_id"]
        }
      },
      "required": ["action", "parameters"]
    },
    description="""
    Call backend MCP service to perform financial operations. 

    Available actions:

    - get_top_transaction_groups
      Description: Query the top transaction groups based on parameters.
      Parameters:
        - startDate (string, required): Start date in ISO 8601 format (e.g., "2023-01-01T00:00:00Z"). Default: "2000-01-01T00:00:00Z"
        - endDate (string, required): End date in ISO 8601 format (e.g., "2023-01-31T23:59:59Z"). Default: "2100-01-31T23:59:59Z"
        - top (integer, required): Maximum number of results to return. Default: 10
        - userId (string, required): User ID to filter results
        - correlationId (string, required): Correlation ID for tracking requests
    """,
    coroutine=mcp_tool_runner,
  )