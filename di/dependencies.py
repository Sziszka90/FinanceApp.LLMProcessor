from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from clients.RabbitMqClient import RabbitMqClient
from services.LoggerService import LoggerService


_rabbitmq_client: IRabbitMqClient | None = None


def get_rabbitmq_client() -> IRabbitMqClient:
    """Return the shared RabbitMQ client."""
    global _rabbitmq_client
    if _rabbitmq_client is None:
        _rabbitmq_client = RabbitMqClient(logger=LoggerService())
    return _rabbitmq_client
