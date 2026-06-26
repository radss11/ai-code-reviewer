from confluent_kafka import Consumer
import json
import os
from dotenv import load_dotenv
from tasks import process_pr

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

def start_consumer():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "code-review-group",
        "auto.offset.reset": "earliest"
    })

    consumer.subscribe(["pr-events"])
    print("Kafka consumer started, waiting for messages...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            data = json.loads(msg.value().decode("utf-8"))
            pr_url = data.get("pr_url")
            print(f"Received PR event: {pr_url}")

            # Trigger Celery task
            process_pr.delay(pr_url)
            print(f"Dispatched Celery task for: {pr_url}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    start_consumer()