import pika
import os
import json

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
EXCHANGE_NAME = os.getenv("RABBITMQ_TOPIC_EXCHANGE_NAME", "llm_processor_exchange")
RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "llm_processor_queue")
MATCH_TRANSACTION_ROUTING_KEY = os.getenv("MATCH_TRANSACTION_ROUTING_KEY", "financeapp.transaction-match")

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials
    )
)

channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
channel.queue_declare(queue=RABBITMQ_QUEUE_NAME, durable=True)
channel.queue_bind(
    exchange=EXCHANGE_NAME,
    queue=RABBITMQ_QUEUE_NAME,
    routing_key=MATCH_TRANSACTION_ROUTING_KEY
)

def publish_to_topic(message: dict, routing_key: str):
    body = json.dumps(message)
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=body.encode('utf-8'),
        properties=pika.BasicProperties(delivery_mode=2)
    )
