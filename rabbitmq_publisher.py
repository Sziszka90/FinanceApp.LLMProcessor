# rabbitmq_publisher.py

import pika
import os
import json


# Example configuration: lists of exchanges, queues, and bindings
EXCHANGES = [e.strip() for e in os.getenv("RABBITMQ_TOPIC_EXCHANGES", "financeapp.llm.topic").split(",")]
QUEUES = [q.strip() for q in os.getenv("RABBITMQ_QUEUES", "financeapp.transactions.queue").split(",")]

# Parse bindings from JSON env var
BINDINGS_JSON = os.getenv("RABBITMQ_BINDINGS", '[{"exchange": "financeapp.llm.topic", "queue": "financeapp.transactions.queue", "routing_key": "financeapp.transactions.*"}]')
BINDINGS = json.loads(BINDINGS_JSON)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

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

def get_exchange_type(exchange: str) -> str:
    match exchange:
        case s if "topic" in s:
            return "topic"
        case s if "direct" in s:
            return "direct"
        case s if "fanout" in s:
            return "fanout"
        case _:
            raise ValueError(f"Unknown exchange type for {exchange}")

for exchange in EXCHANGES:
    channel.exchange_declare(exchange=exchange, exchange_type=get_exchange_type(exchange), durable=True)

for queue in QUEUES:
    channel.queue_declare(queue=queue, durable=True)

for binding in BINDINGS:
    channel.queue_bind(
        exchange=binding["exchange"],
        queue=binding["queue"],
        routing_key=binding["routing_key"]
    )

def publish(exchange: str, routing_key: str, message: dict):
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(message),
    )

