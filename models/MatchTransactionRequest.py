from pydantic import BaseModel, Field, field_validator

class MatchTransactionRequest(BaseModel):
  TransactionNames: list[str] = Field(...)
  TransactionGroupNames: list[str] = Field(...)
  CorrelationId: str = Field(...)
  UserId: str = Field(...)

  @field_validator('TransactionNames')
  def names_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('TransactionNames must not be empty')
    return v

  @field_validator('TransactionGroupNames')
  def group_names_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('TransactionGroupNames must not be empty')
    return v

  @field_validator('CorrelationId')
  def correlation_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('CorrelationId must not be empty')
    return v

  @field_validator('UserId')
  def user_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('UserId must not be empty')
    return v