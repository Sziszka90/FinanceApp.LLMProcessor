from typing import Any, Coroutine
from langchain_core.tools import StructuredTool
from models.McpRequest import McpRequest
from models.McpTopTransactionGroupsRequest import McpTopTransactionGroupsRequest
from tools.abstraction.IMcpTool import IMcpTool
from tools.abstraction.IToolFactory import IToolFactory

class ToolFactory(IToolFactory):
  def __init__(self, mcp_tool: IMcpTool):
    self.mcp_tool = mcp_tool

  def create_top_transaction_groups_tool_runner(self) -> Coroutine[Any, Any, str]:
    async def run_mcp_tool(
      tool_name: str = "GetTopTransactionGroups",
      start_date: str = "2000-01-01T00:00:00Z",
      end_date: str = "2100-01-31T23:59:59Z",
      top: int = 10,
      user_id: str = None,
      correlation_id: str = None
      ):

      if user_id is None:
        raise ValueError("user_id is required")
      if correlation_id is None:
        raise ValueError("correlation_id is required")

      request = McpTopTransactionGroupsRequest(
        tool_name=tool_name,
        start_date=start_date,
        end_date=end_date,
        top=top,
        user_id=user_id,
        correlation_id=correlation_id
      )
      request_dict = request.model_dump() if hasattr(request, 'model_dump') else dict(request)
      request_obj = McpRequest(tool_name=request_dict.pop("tool_name"), parameters=request_dict)
      return await self.mcp_tool.run(mcp_request=request_obj)

    return run_mcp_tool

  def create_top_transaction_groups_tool(self, mcp_tool_runner: Coroutine[Any, Any, str]):
    description = """
    Call the 'GetTopTransactionGroups' MCP tool with the required parameters.
    This tool retrieves the top transaction groups with the most spendings.
    Parameters: 
    startDate: The start date for the transaction groups query.
    endDate: The end date for the transaction groups query.
    top: The maximum number of transaction groups to return.
    """
    return StructuredTool.from_function(
      func=mcp_tool_runner,
      name="GetTopTransactionGroups",
      args_schema=McpTopTransactionGroupsRequest,
      description=description,
      coroutine=mcp_tool_runner,
    )

  def create_tools(self):
    mcp_tool_runner = self.create_top_transaction_groups_tool_runner()
    return [
      self.create_top_transaction_groups_tool(mcp_tool_runner)
    ]