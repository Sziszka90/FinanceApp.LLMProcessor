from typing import List
from pydantic import BaseModel, field_validator, field_validator
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
  Role: str = Field(..., min_length=1, description="Role of the message sender (e.g., 'system', 'user').", alias="role")
  Content: str = Field(..., min_length=1, description="Content of the message.", alias="content")

  @field_validator('Role', 'Content')
  def must_not_be_empty(cls, v, field):
    if not v or not str(v).strip():
      raise ValueError(f'{field.name} must be a non-empty string')
    return v

class ChatMessages(BaseModel):
  Messages: List[ChatMessage]