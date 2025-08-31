from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any

class McpRequest(BaseModel):
	ToolName: str = Field(..., min_length=1, description="The MCP tool to perform on the backend (tool name). Must be a non-empty string.")
	Parameters: Dict[str, Any] = Field(..., description="A dictionary of parameters for the selected MCP tool. Must not be empty.")

	@field_validator('ToolName')
	def tool_name_must_not_be_empty(cls, v):
		if not v or not v.strip():
			raise ValueError('ToolName must be a non-empty string')
		return v

	@field_validator('Parameters')
	def parameters_must_not_be_empty(cls, v):
		if not isinstance(v, dict) or not v:
			raise ValueError('Parameters must be a non-empty dictionary')
		return v
