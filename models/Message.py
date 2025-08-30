from pydantic import BaseModel, field_validator
from pydantic import BaseModel, Field

class Message(BaseModel):
  correlation_id: str = Field(..., min_length=1, description="Correlation ID for the request.", alias="CorrelationId")
  success: bool = Field(..., description="Indicates if the request was successful.", alias="Success")
  error: str = Field(None, description="Error message if the request failed.", alias="Error")
  user_id: str = Field(..., min_length=1, description="User ID associated with the request.", alias="UserId")
  prompt: str = Field(..., min_length=1, description="Prompt sent to the LLM.", alias="Prompt")
  response: str = Field(..., min_length=1, description="Response from the LLM.", alias="Response")

  @field_validator('correlation_id', 'user_id', 'prompt', 'response')
  def must_not_be_empty(cls, v, field):
    if not v or not str(v).strip():
      raise ValueError(f'{field.name} must be a non-empty string')
    return v