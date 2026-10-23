from pydantic import BaseModel, Field, field_validator

class ChatMessage(BaseModel):
  role: str = Field(..., min_length=1, description="Role of the message sender (e.g., 'system', 'user').", alias="Role")
  content: str = Field(..., min_length=1, description="Content of the message.", alias="Content")

  @field_validator('role', 'content')
  def must_not_be_empty(cls, v, info):
    if not v or not str(v).strip():
      raise ValueError(f'{info.field_name} must be a non-empty string')
    return v

  model_config = {"populate_by_name": True, "str_strip_whitespace": True}

class ChatMessages(BaseModel):
  messages: list[ChatMessage] = Field(..., alias="Messages")
  model_config = {"populate_by_name": True, "str_strip_whitespace": True}
