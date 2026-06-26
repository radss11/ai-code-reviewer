from confluent_kafka import Producer
import json
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")


def get_producer():
    return Producer({"bootstrap.servers": KAFKA_BROKER})


async def publish_pr_event(pr_url: str):
    producer = get_producer()
    message = json.dumps({"pr_url": pr_url})
    producer.produce("pr-events", value=message.encode("utf-8"))
    producer.flush()
    print(f"Published PR event: {pr_url}")