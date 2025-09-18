from typing import Any
from pydantic import BaseModel, Field, field_validator

class McpRequest(BaseModel):
	tool_name: str = Field(..., min_length=1, description="The MCP tool to perform on the backend (tool name). Must be a non-empty string.", alias="tool_name")
	parameters: dict[str, Any] = Field(..., description="A dictionary of parameters for the selected MCP tool. Must not be empty.", alias="parameters")

	@field_validator('tool_name')
	def tool_name_must_not_be_empty(cls, v):
		if not v or not v.strip():
			raise ValueError('tool_name must be a non-empty string')
		return v

	@field_validator('parameters')
	def parameters_must_not_be_empty(cls, v):
		if not isinstance(v, dict) or not v:
			raise ValueError('parameters must be a non-empty dictionary')
		return v
