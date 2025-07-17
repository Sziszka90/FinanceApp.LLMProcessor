from pydantic import BaseModel, Field, field_validator
from typing import List

class MatchTransactionRequest(BaseModel):
    transaction_names: List[str] = Field(..., alias="TransactionNames")
    transaction_group_names: List[str] = Field(..., alias="TransactionGroupNames")
    user_id: str = Field(..., alias="UserId")

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