from pydantic import BaseModel
from typing import Dict, Any

class McpRequest(BaseModel):
	name: str
	arguments: Dict[str, Any]
