from pydantic import BaseModel, Field
from typing import Optional

class MCPParameters(BaseModel):
  startDate: Optional[str] = Field(
    default="2000-01-01T00:00:00Z",
    description="The start date for the query in ISO format (YYYY-MM-DDTHH:MM:SSZ). Use 'startDate', not 'start' or 'from_date'."
  )
  endDate: Optional[str] = Field(
    default="2100-01-31T23:59:59Z",
    description="The end date for the query in ISO format (YYYY-MM-DDTHH:MM:SSZ). Use 'endDate', not 'end' or 'to_date'."
  )
  top: Optional[int] = Field(
    default=10,
    description="The number of top results to return. Use 'top', not 'top_n', 'n', or 'limit'."
  )
  userId: str = Field(
    ...,
    description="The unique identifier of the user. Use 'userId', not 'user', 'uid', or 'user_id'."
  )
  correlationId: str = Field(
    ...,
    description="A unique ID for correlating requests. Use 'correlationId', not 'cid' or 'correlation_id'."
  )

class MCPToolRequest(BaseModel):
  action: str = Field(
    ...,
    description="The action to perform on the backend MCP service. Use only the exact parameter names as defined below."
  )
  parameters: MCPParameters = Field(
    ...,
    description="Parameters for the MCP tool request."
  )