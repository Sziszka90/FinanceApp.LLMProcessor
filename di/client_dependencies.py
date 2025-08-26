import injector
from clients.McpClient import McpClient
from clients.RabbitMqClient import RabbitMqClient
from modules.AppModule import AppModule

injector = injector.Injector([AppModule()])

def get_rabbitmq_client() -> RabbitMqClient:
  return injector.get(RabbitMqClient)

def get_mcp_client() -> McpClient:
  return injector.get(McpClient)
