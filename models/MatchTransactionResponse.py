from pydantic import BaseModel, Field

class MatchTransactionResponse(BaseModel):
  transactions: dict[str, str] = Field(..., description="Dictionary of transactions with their matched transaction groups.", alias="transactions")
