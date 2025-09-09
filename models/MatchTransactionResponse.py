from pydantic import BaseModel, Field

class MatchTransactionResponse(BaseModel):
  Transactions: dict[str, str] = Field(..., description="Dictionary of transactions with their matched transaction groups.")
