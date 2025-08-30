from typing import List
from pydantic import BaseModel, field_validator, field_validator
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
  role: str = Field(..., min_length=1, description="Role of the message sender (e.g., 'system', 'user').")
  content: str = Field(..., min_length=1, description="Content of the message.")

  @field_validator('role', 'content')
  def must_not_be_empty(cls, v, field):
    if not v or not str(v).strip():
      raise ValueError(f'{field.name} must be a non-empty string')
    return v

class ChatMessages(BaseModel):
  messages: List[ChatMessage]