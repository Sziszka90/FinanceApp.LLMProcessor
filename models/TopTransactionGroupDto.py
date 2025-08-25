from typing import Optional
from pydantic import BaseModel

class Money(BaseModel):
  amount: float
  currency: str

class TopTransactionGroupDto(BaseModel):
  id: str
  name: str
  description: Optional[str] = None
  group_icon: Optional[str] = None
  total_amount: Money
  transaction_count: int
