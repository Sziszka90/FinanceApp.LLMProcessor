import os
import requests
from langchain.tools import StructuredTool

API_URL = os.getenv("API_URL")

def get_top_transaction_groups(startDate: str, endDate: str, top: int = 10):
    response = requests.get(f"{API_URL}/api/v1/transactiongroups/top", params={
        "startDate": startDate,
        "endDate": endDate,
        "top": top
    })
    return response.json()

get_top_transaction_groups_tool = StructuredTool.from_function(
    func=get_top_transaction_groups,
    name="get_top_transaction_groups",
    description="Fetch top transaction groups for a user.",
    args_schema={
        "startDate": {"type": "string", "description": "The start date for fetching transaction groups."
            " Use format: YYYY-MM-DD"},

        "endDate": {"type": "string", "description": "The end date for fetching transaction groups. "
            "Use format: YYYY-MM-DD"},

        "top": {"type": "integer", "description": "The number of top transaction groups to fetch."}
    }
)