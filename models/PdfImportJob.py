from pydantic import BaseModel, Field


class PdfImportJob(BaseModel):
    correlation_id: str = Field(min_length=1, max_length=200)
    user_id: str = Field(min_length=1, max_length=200)
    filename: str = Field(min_length=1, max_length=255)
    pdf_base64: str = Field(min_length=8, max_length=14_000_000)
    prompt_id: str | None = Field(default=None, max_length=200)
    prompt_name: str | None = Field(default=None, max_length=100)
    prompt: str | None = Field(default=None, max_length=4000)
