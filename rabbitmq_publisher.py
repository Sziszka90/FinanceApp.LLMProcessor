# rabbitmq_publisher.py

import os
from types import SimpleNamespace
import json
import aio_pika
import asyncio

with open("rabbitmq_config.json", "r") as f:
    rabbitmq_config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

HOST_NAME = os.getenv("RABBITMQ_HOST", "localhost")
PORT = int(os.getenv("RABBITMQ_PORT", 5672))
USER_NAME = os.getenv("RABBITMQ_USER", "guest")
PASSWORD = os.getenv("RABBITMQ_PASS", "guest")

async def initialize_rabbitmq_async(max_retries: int = 5, base_wait: int = 5):
    attempt = 0
    while attempt < max_retries:
        try:
            connection = await aio_pika.connect_robust(
                host=HOST_NAME,
                port=PORT,
                virtualhost="/",
                login=USER_NAME,
                password=PASSWORD,
            )
            channel = await connection.channel()

            # Declare exchanges
            for exchange in rabbitmq_config.RabbitMqSettings.Exchanges:
                await channel.declare_exchange(
                    exchange.ExchangeName,
                    type=exchange.ExchangeType,
                    durable=True
                )

            # Declare queues
            for queue in rabbitmq_config.RabbitMqSettings.Queues:
                await channel.declare_queue(queue, durable=True)

            # Bindings
            for binding in rabbitmq_config.RabbitMqSettings.Bindings:
                exch = await channel.get_exchange(binding.Exchange)
                q = await channel.get_queue(binding.Queue)
                await q.bind(exch, routing_key=binding.RoutingKey)

            print("[INFO] RabbitMQ async connection initialized successfully.")
            return connection, channel
        except Exception as e:
            attempt += 1
            wait_time = base_wait * attempt
            print(f"[ERROR] Failed to initialize RabbitMQ async: {e}. Retrying in {wait_time} seconds... ({attempt}/{max_retries})")
            await asyncio.sleep(wait_time)
    raise ConnectionError("Could not connect to RabbitMQ after retries.")

async def publish_async(exchange: str, routing_key: str, message: dict, max_retries: int = 3, base_wait: int = 5):
    attempt = 0
    while attempt < max_retries:
        try:
            connection, channel = await initialize_rabbitmq_async()
            exch = await channel.get_exchange(exchange)
            await exch.publish(
                aio_pika.Message(body=json.dumps(message).encode()),
                routing_key=routing_key
            )
            await connection.close()
            print(f"[INFO] Async message published to {exchange} with routing key {routing_key}")
            break
        except Exception as e:
            attempt += 1
            wait_time = base_wait * attempt
            print(f"[ERROR] Failed to publish async message: {e}. Retrying in {wait_time} seconds... ({attempt}/{max_retries})")
            await asyncio.sleep(wait_time)

