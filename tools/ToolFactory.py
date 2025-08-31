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
        ToolName: str = "GetTopTransactionGroups", 
        StartDate: str = "2000-01-01T00:00:00Z", 
        EndDate: str = "2100-01-31T23:59:59Z", 
        Top: int = 10,
        UserId: str = None,
        CorrelationId: str = None
    ):

      if UserId is None:
        raise ValueError("UserId is required")
      if CorrelationId is None:
        raise ValueError("CorrelationId is required")

      request = McpTopTransactionGroupsRequest(
        ToolName=ToolName,
        StartDate=StartDate,
        EndDate=EndDate,
        Top=Top,
        UserId=UserId,
        CorrelationId=CorrelationId
      )
      request_dict = request.model_dump() if hasattr(request, 'model_dump') else dict(request)
      request_obj = McpRequest(ToolName=request_dict.pop("ToolName"), Parameters=request_dict)
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