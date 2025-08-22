from pydantic import BaseModel, Field, field_validator
from typing import List

class MatchTransactionRequest(BaseModel):
    user_id: str = Field(..., alias="UserId")
    correlation_id: str = Field(..., alias="CorrelationId")
    prompt: str = Field(..., alias="Prompt")

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