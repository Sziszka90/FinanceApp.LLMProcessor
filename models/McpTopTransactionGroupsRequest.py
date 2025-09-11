from pydantic import BaseModel, Field, field_validator

class McpTopTransactionGroupsRequest(BaseModel):
  ToolName: str = Field(..., min_length=1, description="The tool to perform on the backend MCP service. Specify the tool name.")
  StartDate: str = Field(..., min_length=1, description="The start date for the transaction groups query. Default value is 2000-01-01T00:00:00Z")
  EndDate: str = Field(..., min_length=1, description="The end date for the transaction groups query. Default value is 2100-01-31T23:59:59Z")
  Top: int = Field(10, gt=0, description="The maximum number of transaction groups to return.")
  UserId: str = Field(..., min_length=1, description="The ID of the user making the request.")
  CorrelationId: str = Field(..., min_length=1, description="A unique identifier for the request.")

  @field_validator('ToolName', 'StartDate', 'EndDate', 'UserId', 'CorrelationId')
  def must_not_be_empty(cls, v, field):
    if not v or not str(v).strip():
      raise ValueError(f'{field.name} must be a non-empty string')
    return v

  @field_validator('Top')
  def top_must_be_positive(cls, v):
    if v <= 0:
      raise ValueError('Top must be a positive integer')
    return v
