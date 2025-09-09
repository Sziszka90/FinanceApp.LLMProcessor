from typing import TypeVar, Generic
from pydantic.generics import GenericModel

from pydantic import Field, field_validator

T = TypeVar("T")

class Message(GenericModel, Generic[T]):
  CorrelationId: str = Field(..., min_length=1, description="Correlation ID for the request.")
  Success: bool = Field(..., description="Indicates if the request was successful.")
  Error: str = Field(None, description="Error message if the request failed.")
  UserId: str = Field(..., min_length=1, description="User ID associated with the request.")
  Prompt: str = Field(..., min_length=1, description="Prompt sent to the LLM.")
  Response: T = Field(..., description="Response from the LLM.")

  @field_validator('CorrelationId', 'UserId', 'Prompt')
  def must_not_be_empty(cls, v, field):
    if not v or not str(v).strip():
      raise ValueError(f'{field.name} must be a non-empty string')
    return v