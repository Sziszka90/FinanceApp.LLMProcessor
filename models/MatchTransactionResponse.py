from pydantic import BaseModel, Field

class MatchTransactionResponse(BaseModel):
  transactions: list[dict[str, str]] = Field(..., description="List of transactions with their matched transaction groups.")
