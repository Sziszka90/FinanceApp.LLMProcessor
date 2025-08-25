from langchain_core.tools import StructuredTool
from di.dependencies import get_top_transaction_groups_sync

get_top_transaction_groups_tool = StructuredTool.from_function(
  func=get_top_transaction_groups_sync,
  name="get_top_transaction_groups",
  description="Fetch top transaction groups for a user within a date range."
)
