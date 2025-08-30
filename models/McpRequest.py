from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any

class McpRequest(BaseModel):
	action: str = Field(..., min_length=1, description="The MCP action to perform on the backend (tool name). Must be a non-empty string.")
	parameters: Dict[str, Any] = Field(..., description="A dictionary of parameters for the selected MCP action. Must not be empty.")

	@field_validator('action')
	def action_must_not_be_empty(cls, v):
		if not v or not v.strip():
			raise ValueError('action must be a non-empty string')
		return v

	@field_validator('parameters')
	def parameters_must_not_be_empty(cls, v):
		if not isinstance(v, dict) or not v:
			raise ValueError('parameters must be a non-empty dictionary')
		return v
