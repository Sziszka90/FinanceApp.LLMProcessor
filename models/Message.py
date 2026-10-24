from typing import TypeVar, Generic
from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")

class Message(BaseModel, Generic[T]):
  correlation_id: str = Field(..., min_length=1, description="Correlation ID for the request.", alias="correlation_id")
  success: bool = Field(..., description="Indicates if the request was successful.", alias="success")
  error: str | None = Field(default=None, description="Error message if the request failed.", alias="error")
  user_id: str = Field(..., min_length=1, description="User ID associated with the request.", alias="user_id")
  prompt: str = Field(..., min_length=1, description="Prompt sent to the LLM.", alias="prompt")
  data: T | None = Field(default=None, alias="data")

  @field_validator('correlation_id', 'user_id', 'prompt')
  def must_not_be_empty(cls, v, info):
    if not v or not str(v).strip():
      raise ValueError(f'{info.field_name} must be a non-empty string')
    return v
