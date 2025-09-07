from pydantic import BaseModel, Field
from typing import List, Dict

class MatchTransactionResponse(BaseModel):
  transactions: List[Dict[str, str]] = Field(..., description="List of transactions with their matched transaction groups.")
