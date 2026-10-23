from typing import Any
from pydantic import BaseModel, Field, field_validator

class McpEnvelope(BaseModel):
	tool_name: str = Field(..., min_length=1, description="Name of the MCP tool executed.", alias="toolName")
	payload: Any = Field(..., description="Payload returned by the MCP tool.", alias="payload")

	@field_validator('tool_name')
	def tool_name_must_not_be_empty(cls, v):
		if not v or not v.strip():
			raise ValueError('tool_name must be a non-empty string')
		return v

	@field_validator('payload')
	def payload_must_exist(cls, v):
		if v is None:
			raise ValueError('payload must not be None')
		return v
