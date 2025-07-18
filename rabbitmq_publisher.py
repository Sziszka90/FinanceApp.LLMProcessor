
# rabbitmq_publisher.py

import pika
import os
import json

def initialize_rabbitmq():
    RABBITMQ_TOPIC_EXCHANGES='[{"exchange": "financeapp.llm.topic", "exchange_type": "topic"}]'
    RABBITMQ_QUEUES='[{"queue": "financeapp.transactions.queue"}]'
    RABBITMQ_BINDINGS='[{"exchange": "financeapp.llm.topic", "queue": "financeapp.transactions.queue", "routing_key": "financeapp.transactions.*"}]'
    EXCHANGES = json.loads(RABBITMQ_TOPIC_EXCHANGES)
    QUEUES = [q["queue"] for q in json.loads(RABBITMQ_QUEUES)]
    BINDINGS = json.loads(RABBITMQ_BINDINGS)
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_VHOST = "/"
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")


    global connection, channel
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
            credentials=pika.PlainCredentials(
                username=RABBITMQ_USER,
                password=RABBITMQ_PASS
            )
        )
    )
    channel = connection.channel()


    for exchange_obj in EXCHANGES:
        channel.exchange_declare(
            exchange=exchange_obj["exchange"],
            exchange_type=exchange_obj["exchange_type"],
            durable=True
        )

    for queue in QUEUES:
        channel.queue_declare(queue=queue, durable=True)

    for binding in BINDINGS:
        channel.queue_bind(
            exchange=binding["exchange"],
            queue=binding["queue"],
            routing_key=binding["routing_key"]
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

