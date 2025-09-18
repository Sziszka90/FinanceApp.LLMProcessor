from pydantic import BaseModel, Field, field_validator

class MatchTransactionRequest(BaseModel):
  transaction_names: list[str] = Field(..., alias="TransactionNames")
  transaction_group_names: list[str] = Field(..., alias="TransactionGroupNames")
  correlation_id: str = Field(..., alias="CorrelationId")
  user_id: str = Field(..., alias="UserId")

  @field_validator('transaction_names')
  def names_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('transaction_names must not be empty')
    return v

  @field_validator('transaction_group_names')
  def group_names_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('transaction_group_names must not be empty')
    return v

  @field_validator('correlation_id')
  def correlation_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('correlation_id must not be empty')
    return v

  @field_validator('user_id')
  def user_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('user_id must not be empty')
    return v