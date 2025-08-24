tools = [
  {
    "name": "get_top_transaction_groups",
    "description": "Fetch top transaction groups for a user within a date range.",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {"type": "string"},
        "start_date": {"type": "string"},
        "end_date": {"type": "string"},
        "top": {"type": "integer"}
      },
      "required": ["user_id", "start_date", "end_date", "top"]
    },
  }
]