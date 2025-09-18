from pydantic import BaseModel, Field, field_validator

class McpTopTransactionGroupsRequest(BaseModel):
  tool_name: str = Field(..., alias="tool_name", min_length=1, description="The tool to perform on the backend MCP service. Specify the tool name.")
  start_date: str = Field(..., alias="start_date", min_length=1, description="The start date for the transaction groups query. Default value is 2000-01-01T00:00:00Z")
  end_date: str = Field(..., alias="end_date", min_length=1, description="The end date for the transaction groups query. Default value is 2100-01-31T23:59:59Z")
  user_id: str = Field(..., alias="user_id", min_length=1, description="The ID of the user making the request.")
  correlation_id: str = Field(..., alias="correlation_id", min_length=1, description="A unique identifier for the request.")
  top: int = Field(10, alias="top", gt=0, description="The maximum number of transaction groups to return.")

  @field_validator('tool_name', 'start_date', 'end_date', 'user_id', 'correlation_id')
  def must_not_be_empty(cls, v, field):
    if not v or not str(v).strip():
      raise ValueError(f'{field.name} must be a non-empty string')
    return v

  @field_validator('top')
  def top_must_be_positive(cls, v):
    if v <= 0:
      raise ValueError('top must be a positive integer')
    return v
