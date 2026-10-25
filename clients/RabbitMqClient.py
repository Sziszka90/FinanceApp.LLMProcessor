import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import aio_pika

from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from services.abstraction.ILoggerService import ILoggerService
from config.settings import get_settings


class RabbitMqClient(IRabbitMqClient):
    def __init__(self, logger: ILoggerService):
        self.logger = logger
        self.connection = None
        self.channel = None
        settings = get_settings()
        self.host = settings.rabbitmq_host
        self.port = settings.rabbitmq_port
        self.user = settings.rabbitmq_user
        self.password = settings.rabbitmq_pass

        config_path = Path(__file__).resolve().parent.parent / "rabbitmq_config.json"
        with config_path.open(encoding="utf-8") as config_file:
            self.rabbitmq_config = json.load(
                config_file, object_hook=lambda value: SimpleNamespace(**value)
            )

    async def initialize_async(self, max_retries: int = 5, base_wait: int = 5):
        if self.connection and not self.connection.is_closed:
            return self.connection, self.channel

        for attempt in range(1, max_retries + 1):
            try:
                self.connection = await aio_pika.connect_robust(
                    host=self.host,
                    port=self.port,
                    virtualhost="/",
                    login=self.user,
                    password=self.password,
                )
                self.channel = await self.connection.channel()

                rabbitmq_settings = self.rabbitmq_config.RabbitMqSettings
                pdf_request_retry_queue = f"{rabbitmq_settings.PdfRequestQueue}.retry"
                match_result_retry_queue = f"{rabbitmq_settings.ResultQueue}.retry"
                match_result_dead_letter_queue = f"{rabbitmq_settings.ResultQueue}.dead"
                queue_names = (
                    rabbitmq_settings.RequestQueue,
                    rabbitmq_settings.ResultQueue,
                    rabbitmq_settings.DeadLetterQueue,
                    match_result_retry_queue,
                    match_result_dead_letter_queue,
                    rabbitmq_settings.PdfRequestQueue,
                    pdf_request_retry_queue,
                    rabbitmq_settings.PdfResultQueue,
                    rabbitmq_settings.PdfDeadLetterQueue,
                )
                for queue_name in queue_names:
                    arguments = None
                    if queue_name == rabbitmq_settings.RequestQueue:
                        arguments = {
                            "x-dead-letter-exchange": "",
                            "x-dead-letter-routing-key": rabbitmq_settings.DeadLetterQueue,
                        }
                    elif queue_name == rabbitmq_settings.PdfRequestQueue:
                        arguments = {
                            "x-dead-letter-exchange": "",
                            "x-dead-letter-routing-key": rabbitmq_settings.PdfDeadLetterQueue,
                        }
                    elif queue_name == pdf_request_retry_queue:
                        arguments = {
                            "x-message-ttl": 10000,
                            "x-dead-letter-exchange": "",
                            "x-dead-letter-routing-key": rabbitmq_settings.PdfRequestQueue,
                        }
                    elif queue_name == match_result_retry_queue:
                        arguments = {
                            "x-message-ttl": 10000,
                            "x-dead-letter-exchange": "",
                            "x-dead-letter-routing-key": rabbitmq_settings.ResultQueue,
                        }
                    await self.channel.declare_queue(
                        queue_name,
                        durable=True,
                        arguments=arguments,
                    )

                self.logger.info("RabbitMQ async connection established")
                return self.connection, self.channel
            except Exception as error:
                wait_time = base_wait * attempt
                self.logger.warning(
                    "RabbitMQ connection failed (%s); retrying in %s seconds (%s/%s)",
                    type(error).__name__,
                    wait_time,
                    attempt,
                    max_retries,
                )
                if attempt < max_retries:
                    await asyncio.sleep(wait_time)

        raise ConnectionError("Could not connect to RabbitMQ after retries")

    async def publish_to_queue_async(
        self,
        queue_name: str,
        message: dict[str, Any],
        max_retries: int = 3,
        base_wait: int = 5,
        headers: dict[str, Any] | None = None,
    ) -> None:
        for attempt in range(1, max_retries + 1):
            try:
                await self.initialize_async()
                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(message).encode(),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        headers=headers,
                    ),
                    routing_key=queue_name,
                )
                self.logger.info(
                    "Message published to queue %s",
                    queue_name,
                )
                return
            except Exception as error:
                wait_time = base_wait * attempt
                self.logger.warning(
                    "RabbitMQ publish failed (%s); retrying in %s seconds (%s/%s)",
                    type(error).__name__,
                    wait_time,
                    attempt,
                    max_retries,
                )
                if attempt < max_retries:
                    await asyncio.sleep(wait_time)

        raise ConnectionError("Could not publish RabbitMQ message after retries")

    async def consume_async(
        self,
        queue_name: str,
        callback: Callable[[Any], Awaitable[None]],
    ) -> None:
        await self.initialize_async()
        queue = await self.channel.get_queue(queue_name)
        await self.channel.set_qos(prefetch_count=1)
        await queue.consume(callback, no_ack=False)
        self.logger.info("Consuming RabbitMQ queue %s", queue_name)

    async def close_async(self) -> None:
        if self.connection is not None and not self.connection.is_closed:
            await self.connection.close()
        self.connection = None
        self.channel = None
