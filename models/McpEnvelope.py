from pydantic import BaseModel
from typing import Any

class McpEnvelope(BaseModel):
	tool_name: str
	payload: Any
