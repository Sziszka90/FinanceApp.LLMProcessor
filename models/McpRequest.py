from pydantic import BaseModel
from typing import Dict, Any

class McpRequest(BaseModel):
	action: str
	parameters: Dict[str, Any]
