from pydantic import BaseModel, validator
from typing import List

class MatchTransactionRequest(BaseModel):
    transaction_names: List[str]
    transaction_group_names: List[str]

    @validator('transaction_names')
    def names_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('transaction_names must not be empty')
        return v

    @validator('transaction_group_names')
    def group_names_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('transaction_group_names must not be empty')
        return v
