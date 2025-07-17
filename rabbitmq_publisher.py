# rabbitmq_publisher.py

import pika
import os
import json

EXCHANGE_NAME = os.getenv("RABBITMQ_TOPIC_EXCHANGE_NAME", "llm_processor_topic_exchange")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "llm_processor_queue")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# Initialize connection and channel once
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
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="financeapp.transactions.*")

def publish_to_topic(routing_key: str, message: dict):
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=json.dumps(message),
    )
