from pydantic import BaseModel, Field


class MatchTransactionJob(BaseModel):
    transaction_names: list[str] = Field(min_length=1, max_length=500)
    transaction_group_names: list[str] = Field(min_length=1, max_length=200)
    user_id: str = Field(min_length=1, max_length=200)
    correlation_id: str = Field(min_length=1, max_length=200)
    model_config = {"str_strip_whitespace": True}
