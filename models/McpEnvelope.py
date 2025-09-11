from pydantic import BaseModel, Field, field_validator

class McpEnvelope(BaseModel):
	ToolName: str = Field(..., min_length=1, description="Name of the MCP tool executed.")
	Payload: any = Field(..., description="Payload returned by the MCP tool.")

	@field_validator('ToolName')
	def tool_name_must_not_be_empty(cls, v):
		if not v or not v.strip():
			raise ValueError('Tool must be a non-empty string')
		return v

	@field_validator('Payload')
	def payload_must_exist(cls, v):
		if v is None:
			raise ValueError('Payload must not be None')
		return v
