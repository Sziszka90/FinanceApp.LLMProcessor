from pydantic import BaseModel, Field, field_validator
from typing import List

class MatchTransactionRequest(BaseModel):
  transaction_names: List[str] = Field(..., alias="TransactionNames")
  transaction_group_names: List[str] = Field(..., alias="TransactionGroupNames")
  correlation_id: str = Field(..., alias="CorrelationId")

  @field_validator('transaction_names')
  def names_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('TransactionNames must not be empty')
    return v

  @field_validator('transaction_group_names')
  def group_names_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('TransactionGroupNames must not be empty')
    return v
  
  @field_validator('correlation_id')
  def correlation_id_must_not_be_empty(cls, v):
    if not v:
      raise ValueError('CorrelationId must not be empty')
    return v