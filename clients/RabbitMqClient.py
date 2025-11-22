
import os
from types import SimpleNamespace
import json
import aio_pika
import asyncio
from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from services.abstraction.ILoggerService import ILoggerService

class RabbitMqClient(IRabbitMqClient):
  def __init__(self, logger: ILoggerService):
    self.logger = logger
    self.connection = None
    self.channel = None

    self.host = os.getenv("RABBITMQ_HOST", "localhost")
    self.port = int(os.getenv("RABBITMQ_PORT", 5672))
    self.user = os.getenv("RABBITMQ_USER", "guest")
    self.password = os.getenv("RABBITMQ_PASS", "guest")

    with open("rabbitmq_config.json", "r") as f:
      self.rabbitmq_config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

  async def initialize_async(self, max_retries: int = 5, base_wait: int = 5):

    if self.connection and not self.connection.is_closed:
      return self.connection, self.channel

    attempt = 0

    while attempt < max_retries:
      try:
        self.connection = await aio_pika.connect_robust(
          host=self.host,
          port=self.port,
          virtualhost="/",
          login=self.user,
          password=self.password,
        )
        self.channel = await self.connection.channel()

        for exchange in self.rabbitmq_config.RabbitMqSettings.Exchanges:
          await self.channel.declare_exchange(
            exchange.ExchangeName,
            type=exchange.ExchangeType,
            durable=True
          )

        for queue in self.rabbitmq_config.RabbitMqSettings.Queues:
          await self.channel.declare_queue(queue, durable=True)

        for binding in self.rabbitmq_config.RabbitMqSettings.Bindings:
          exch = await self.channel.get_exchange(binding.Exchange)
          q = await self.channel.get_queue(binding.Queue)
          await q.bind(exch, routing_key=binding.RoutingKey)

        self.logger.info("RabbitMQ async connection established")
        
        return self.connection, self.channel
      
      except Exception as e:
        attempt += 1
        wait_time = base_wait * attempt
        
        self.logger.warning(f"Failed to connect to RabbitMQ: {e}. Retrying in {wait_time} seconds... ({attempt}/{max_retries})")
        
        await asyncio.sleep(wait_time)

    self.logger.error("Could not connect to RabbitMQ after retries.")
    raise ConnectionError("Could not connect to RabbitMQ after retries.")

  async def publish_async(self, exchange: str, routing_key: str, message: dict, max_retries: int = 3, base_wait: int = 5):
    attempt = 0

    while attempt < max_retries:
      try:
        # Ensure connection is ready
        await self.initialize_async()
        
        exch = await self.channel.get_exchange(exchange)
        await exch.publish(
          aio_pika.Message(body=json.dumps(message).encode()),
          routing_key=routing_key
        )

        self.logger.info(f"Message published to exchange {exchange} with routing key {routing_key}")
        
        break
     
      except Exception as e:
        attempt += 1
        wait_time = base_wait * attempt

        self.logger.warning(f"Failed to publish async message: {e}. Retrying in {wait_time} seconds... ({attempt}/{max_retries})")

        await asyncio.sleep(wait_time)