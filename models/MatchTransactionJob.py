from pydantic import BaseModel, Field


class CategorizationRule(BaseModel):
    merchant_text: str = Field(min_length=2, max_length=200)
    transaction_group_name: str = Field(min_length=1, max_length=255)


class MatchTransactionJob(BaseModel):
    transaction_names: list[str] = Field(min_length=1, max_length=500)
    transaction_group_names: list[str] = Field(min_length=1, max_length=200)
    categorization_rules: list[CategorizationRule] = Field(default_factory=list, max_length=500)
    user_id: str = Field(min_length=1, max_length=200)
    correlation_id: str = Field(min_length=1, max_length=200)
    model_config = {"str_strip_whitespace": True}
