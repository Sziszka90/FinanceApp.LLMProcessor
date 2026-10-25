import logging

from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError

from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from models.MatchTransactionJob import MatchTransactionJob
from services.LLMService import LLMService
from services.LoggerService import LoggerService
from services.PromptService import PromptService


class MatchTransactionJobHandler:
    def __init__(self, rabbitmq_client: IRabbitMqClient) -> None:
        self.rabbitmq_client = rabbitmq_client
        self.logger = logging.getLogger(__name__)

    async def handle(self, message: AbstractIncomingMessage) -> None:
        try:
            job = MatchTransactionJob.model_validate_json(message.body)
        except ValidationError:
            self.logger.error("Discarding invalid transaction matching job")
            await message.reject(requeue=False)
            return

        async with message.process(requeue=True):
            logger = LoggerService()
            llm_service = LLMService(
                rabbitmq_client=self.rabbitmq_client,
                logger=logger,
                prompt_service=PromptService(),
            )
            await llm_service.match_transactions(
                correlation_id=job.correlation_id,
                transaction_names=job.transaction_names,
                transaction_group_names=job.transaction_group_names,
                categorization_rules=[rule.model_dump() for rule in job.categorization_rules],
                user_id=job.user_id,
            )
