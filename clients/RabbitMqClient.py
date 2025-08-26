
import os
from types import SimpleNamespace
import json
import aio_pika
import asyncio

class RabbitMqClient:
  def __init__(self, config_path: str = "rabbitmq_config.json"):

    with open(config_path, "r") as f:
      self.rabbitmq_config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

    self.host = os.getenv("RABBITMQ_HOST", "localhost")
    self.port = int(os.getenv("RABBITMQ_PORT", 5672))
    self.user = os.getenv("RABBITMQ_USER", "guest")
    self.password = os.getenv("RABBITMQ_PASS", "guest")

  async def initialize_async(self, max_retries: int = 5, base_wait: int = 5):
    attempt = 0

    while attempt < max_retries:
      try:
        connection = await aio_pika.connect_robust(
          host=self.host,
          port=self.port,
          virtualhost="/",
          login=self.user,
          password=self.password,
        )
        channel = await connection.channel()

        for exchange in self.rabbitmq_config.RabbitMqSettings.Exchanges:
          await channel.declare_exchange(
            exchange.ExchangeName,
            type=exchange.ExchangeType,
            durable=True
          )

        for queue in self.rabbitmq_config.RabbitMqSettings.Queues:
          await channel.declare_queue(queue, durable=True)

        for binding in self.rabbitmq_config.RabbitMqSettings.Bindings:
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

  async def publish_async(self, exchange: str, routing_key: str, message: dict, max_retries: int = 3, base_wait: int = 5):
    attempt = 0

    while attempt < max_retries:
      try:
        connection, channel = await self.initialize_async()
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