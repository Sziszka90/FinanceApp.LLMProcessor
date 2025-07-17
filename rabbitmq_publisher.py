# rabbitmq_publisher.py

import pika
import os
import json

EXCHANGE_NAME = os.getenv("RABBITMQ_TOPIC_EXCHANGE_NAME", "llm_processor_topic_exchange")

def publish_to_topic(routing_key: str, message: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", 5672)),
            virtual_host=os.getenv("RABBITMQ_VHOST", "/"),
            credentials=pika.PlainCredentials(
                username=os.getenv("RABBITMQ_USER", "guest"),
                password=os.getenv("RABBITMQ_PASS", "guest")
            )
        )
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)

    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=json.dumps(message)
    )

    connection.close()
