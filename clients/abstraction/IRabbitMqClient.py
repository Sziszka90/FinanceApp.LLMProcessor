from abc import ABC, abstractmethod

class IRabbitMqClient(ABC):
  @abstractmethod
  async def initialize_async(self, max_retries: int = 5, base_wait: int = 5):
    """
    Initializes the RabbitMQ client asynchronously.
    """
    pass

  @abstractmethod
  async def publish_async(self, exchange: str, routing_key: str, message: dict, max_retries: int = 3, base_wait: int = 5):
    """
    Publishes a message to the specified RabbitMQ exchange and routing key.
    """
    pass
