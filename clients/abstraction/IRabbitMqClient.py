from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any

class IRabbitMqClient(ABC):
  rabbitmq_config: Any
  @abstractmethod
  async def initialize_async(self, max_retries: int = 5, base_wait: int = 5):
    """
    Initializes the RabbitMQ client asynchronously.
    """
    pass

  @abstractmethod
  async def publish_to_queue_async(
    self,
    queue_name: str,
    message: dict,
    max_retries: int = 3,
    base_wait: int = 5,
    headers: dict[str, Any] | None = None,
  ):
    """
    Publishes a message to the specified RabbitMQ exchange and routing key.
    """
    pass

  @abstractmethod
  async def close_async(self) -> None:
    """Close the connection during application shutdown."""
    pass

  @abstractmethod
  async def consume_async(
    self,
    queue_name: str,
    callback: Callable[[Any], Awaitable[None]],
  ) -> None:
    """Register the callback to consume messages from a durable queue."""
    pass
