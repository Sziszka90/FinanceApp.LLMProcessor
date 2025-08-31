from pydantic import BaseModel, Field, field_validator

class PromptRequest(BaseModel):
  Prompt: str = Field(...)
  UserId: str = Field(None)
  CorrelationId: str = Field(...)

  @field_validator('Prompt')
  def prompt_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('Prompt must not be empty')
    return v

  @field_validator('UserId')
  def user_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('UserId must not be empty')
    return v

  @field_validator('CorrelationId')
  def correlation_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('CorrelationId must not be empty')
    return v