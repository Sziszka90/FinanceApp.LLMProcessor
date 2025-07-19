
# rabbitmq_publisher.py

from types import SimpleNamespace
import pika
import json

with open("rabbitmq_config.json", "r") as f:
    rabbitmq_config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

def initialize_rabbitmq():
    global connection, channel
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_config.RabbitMqSettings.HostName,
            port=rabbitmq_config.RabbitMqSettings.Port,
            virtual_host="/",
            credentials=pika.PlainCredentials(
                username=rabbitmq_config.RabbitMqSettings.UserName,
                password=rabbitmq_config.RabbitMqSettings.Password
            )
        )
    )
    channel = connection.channel()

    for exchange in rabbitmq_config.RabbitMqSettings.Exchanges:
        channel.exchange_declare(
            exchange=exchange.ExchangeName,
            exchange_type=exchange.ExchangeType,
            durable=True
        )

    for queue in rabbitmq_config.RabbitMqSettings.Queues:
        channel.queue_declare(queue=queue, durable=True)

    for binding in rabbitmq_config.RabbitMqSettings.Bindings:
        channel.queue_bind(
            exchange=binding.Exchange,
            queue=binding.Queue,
            routing_key=binding.RoutingKey
        )


initialize_rabbitmq()

def publish(exchange: str, routing_key: str, message: dict, max_retries: int = 3):
    global connection, channel
    attempt = 0
    while attempt < max_retries:
        try:
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message),
            )
            print(f"[INFO] Message published to {exchange} with routing key {routing_key}")
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[WARN] RabbitMQ connection lost, retrying... ({attempt+1}/{max_retries})")          
            try:
                initialize_rabbitmq()
            except Exception as conn_e:
                print(f"[ERROR] Failed to reconnect to RabbitMQ: {conn_e}")
            attempt += 1
        except Exception as e:
            print(f"[ERROR] Failed to publish message: {e}")
            break

