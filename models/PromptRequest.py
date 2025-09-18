from pydantic import BaseModel, Field, field_validator

class PromptRequest(BaseModel):
  prompt: str = Field(..., alias="prompt")
  user_id: str = Field(None, alias="userId")
  correlation_id: str = Field(..., alias="correlationId")

  @field_validator('prompt')
  def prompt_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('prompt must not be empty')
    return v

  @field_validator('user_id')
  def user_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('user_id must not be empty')
    return v

  @field_validator('correlation_id')
  def correlation_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('correlation_id must not be empty')
    return v