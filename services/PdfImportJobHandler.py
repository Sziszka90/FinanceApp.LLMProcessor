import base64
import logging
from decimal import Decimal
from typing import Any

from aio_pika.abc import AbstractIncomingMessage
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from config.settings import get_settings
from models.PdfImportJob import PdfImportJob
from services.abstraction.IPromptService import IPromptService


NULLABLE_DECIMAL = {"anyOf": [{"type": "string"}, {"type": "null"}]}
NULLABLE_STRING = {"anyOf": [{"type": "string"}, {"type": "null"}]}
PDF_RETRY_COUNT_HEADER = "x-financeapp-pdf-processing-retries"
MAX_PDF_PROCESSING_RETRIES = 3

STATEMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "statementCurrency": {"type": "string"},
        "openingBalance": NULLABLE_DECIMAL,
        "closingBalance": NULLABLE_DECIMAL,
        "totalDebits": NULLABLE_DECIMAL,
        "totalCredits": NULLABLE_DECIMAL,
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "details": NULLABLE_STRING,
                    "date": {"type": "string"},
                    "signedAmount": {"type": "string"},
                    "currency": {"type": "string"},
                    "reference": NULLABLE_STRING,
                    "pageNumber": {"type": "integer"},
                },
                "required": ["description", "details", "date", "signedAmount", "currency", "reference", "pageNumber"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["statementCurrency", "openingBalance", "closingBalance", "totalDebits", "totalCredits", "transactions"],
    "additionalProperties": False,
}


class PdfTransaction(BaseModel):
    description: str = Field(min_length=1)
    details: str | None
    date: str
    signedAmount: Decimal
    currency: str
    reference: str | None
    pageNumber: int = Field(ge=1)


class PdfStatement(BaseModel):
    statementCurrency: str
    openingBalance: Decimal | None
    closingBalance: Decimal | None
    totalDebits: Decimal | None
    totalCredits: Decimal | None
    transactions: list[PdfTransaction] = Field(min_length=1, max_length=500)


class PdfImportJobHandler:
    def __init__(
        self,
        rabbitmq_client: IRabbitMqClient,
        prompt_service: IPromptService,
    ) -> None:
        self.rabbitmq_client = rabbitmq_client
        self.prompt_service = prompt_service
        self.logger = logging.getLogger(__name__)

    async def handle(self, message: AbstractIncomingMessage) -> None:
        try:
            job = PdfImportJob.model_validate_json(message.body)
        except ValidationError:
            self.logger.error("Discarding invalid PDF import job")
            await message.reject(requeue=False)
            return

        async with message.process(requeue=False):
            result_queue = self.rabbitmq_client.rabbitmq_config.RabbitMqSettings.PdfResultQueue
            retry_queue = f"{self.rabbitmq_client.rabbitmq_config.RabbitMqSettings.PdfRequestQueue}.retry"
            retry_count = self._get_retry_count(message.headers)
            try:
                await self.rabbitmq_client.publish_to_queue_async(result_queue, {
                    "correlation_id": job.correlation_id,
                    "user_id": job.user_id,
                    "status": "processing",
                })

                pdf = base64.b64decode(job.pdf_base64, validate=True)
                if len(pdf) > 10 * 1024 * 1024 or not pdf.startswith(b"%PDF-"):
                    raise ValueError("Invalid PDF document")

                settings = get_settings()
                endpoint = settings.azure_openai_endpoint
                deployment = settings.azure_openai_pdf_deployment_name or settings.azure_openai_deployment_name
                api_key = settings.azure_openai_api_key or settings.openai_api_key
                if not endpoint or not deployment or not api_key:
                    raise ValueError("Azure OpenAI configuration is incomplete")
                base_url = endpoint.rstrip("/")
                if not base_url.endswith("/openai/v1"):
                    base_url += "/openai/v1"

                async with AsyncOpenAI(base_url=base_url + "/", api_key=api_key) as client:
                    response = await client.responses.create(
                        model=deployment,
                        instructions=self.prompt_service.get_pdf_import_system_prompt(),
                        input=[{
                            "role": "user",
                            "content": [
                                {"type": "input_file", "filename": "statement.pdf",
                                 "file_data": "data:application/pdf;base64," + job.pdf_base64},
                                {
                                    "type": "input_text",
                                    "text": self.prompt_service.get_pdf_import_user_prompt(job.prompt),
                                },
                            ],
                        }],
                        text={"format": {"type": "json_schema", "name": "bank_statement",
                                         "strict": True, "schema": STATEMENT_SCHEMA}},
                        max_output_tokens=20000,
                        store=False,
                    )
                if not response.output_text:
                    raise ValueError("Model returned no statement data")
                statement = PdfStatement.model_validate_json(response.output_text)
                result = {"correlation_id": job.correlation_id, "user_id": job.user_id,
                          "success": True, "data": statement.model_dump(mode="json")}
                await self.rabbitmq_client.publish_to_queue_async(result_queue, result)
                self.logger.info("Extracted %s transactions for PDF import %s",
                                 len(statement.transactions), job.correlation_id)
            except Exception as error:
                self.logger.error("PDF extraction failed for %s (attempt %s/%s, %s): %s",
                                  job.correlation_id, retry_count + 1, MAX_PDF_PROCESSING_RETRIES + 1,
                                  type(error).__name__, error)
                if retry_count < MAX_PDF_PROCESSING_RETRIES:
                    await self.rabbitmq_client.publish_to_queue_async(
                        retry_queue,
                        job.model_dump(mode="json"),
                        headers={PDF_RETRY_COUNT_HEADER: retry_count + 1},
                    )
                    self.logger.info("Scheduled automatic PDF retry %s/%s for %s",
                                     retry_count + 1, MAX_PDF_PROCESSING_RETRIES, job.correlation_id)
                    return

                await self.rabbitmq_client.publish_to_queue_async(result_queue, {
                    "correlation_id": job.correlation_id,
                    "user_id": job.user_id,
                    "success": False,
                    "error": "PDF extraction failed after 3 automatic retries. Check the PDF and model configuration.",
                })

    @staticmethod
    def _get_retry_count(headers: dict[str, Any] | None) -> int:
        if not headers:
            return 0
        value = headers.get(PDF_RETRY_COUNT_HEADER, 0)
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0
