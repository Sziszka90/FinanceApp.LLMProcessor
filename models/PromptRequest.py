from pydantic import BaseModel, Field, field_validator

class PromptRequest(BaseModel):
  prompt: str = Field(..., alias="Prompt")
  user_id: str = Field(None, alias="UserId")
  correlation_id: str = Field(..., alias="CorrelationId")

  @field_validator('prompt')
  def prompt_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('Prompt must not be empty')
    return v

  @field_validator('user_id')
  def user_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('UserId must not be empty')
    return v

  @field_validator('correlation_id')
  def correlation_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('CorrelationId must not be empty')
    return v