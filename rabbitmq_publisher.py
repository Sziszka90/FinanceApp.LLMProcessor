# rabbitmq_publisher.py

from types import SimpleNamespace
import pika
import json
import time

with open("rabbitmq_config.json", "r") as f:
    rabbitmq_config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

def initialize_rabbitmq(max_retries: int = 5, base_wait: int = 5):
    global connection, channel
    attempt = 0
    while attempt < max_retries:
        try:
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
            print("[INFO] RabbitMQ connection initialized successfully.")
            break
        except pika.exceptions.AMQPConnectionError as e:
            attempt += 1
            wait_time = base_wait * attempt
            print(f"[WARN] Failed to connect to RabbitMQ, retrying in {wait_time} seconds... ({attempt}/{max_retries})")
            time.sleep(wait_time)
        except Exception as e:
            attempt += 1
            wait_time = base_wait * attempt
            print(f"[ERROR] Unexpected error initializing RabbitMQ: {e}. Retrying in {wait_time} seconds... ({attempt}/{max_retries})")
            time.sleep(wait_time)

def publish(exchange: str, routing_key: str, message: dict, max_retries: int = 3, base_wait: int = 5):
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
            wait_time = base_wait * attempt
            print(f"[INFO] Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"[ERROR] Failed to publish message: {e}")
            attempt += 1
            wait_time = base_wait * attempt
            print(f"[INFO] Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)

