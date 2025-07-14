# consumer/consumer.py
import json
import pandas as pd
from io import BytesIO
from kafka import KafkaConsumer
from datetime import datetime, timedelta
import time
import signal
import sys
import os
import boto3
from dotenv import load_dotenv
import toml

load_dotenv()
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
app_config = toml.load('config_file.toml')
S3_BUCKET = app_config['aws']['bucket_name']
aws_region = app_config['aws']['aws_region']

session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)
s3_client = session.client('s3')

# Graceful shutdown flag
running = True

def upload_fileobj(bucket, key, file_obj):
    file_obj.seek(0)
    s3_client.upload_fileobj(file_obj, bucket, key)

def signal_handler(sig, frame):
    global running
    print("\n[Consumer] Shutdown signal received. Preparing to exit...")
    running = False

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    "weather-data",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id="weather-consumer-group",
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

buffer = []
last_write_time = datetime.utcnow()

print("Starting Kafka consumer...")

try:
    while running:
        # Poll Kafka every 1 second
        records = consumer.poll(timeout_ms=1000)
        
        if not records:
            print('Records do not exist')

        for topic_partition, messages in records.items():
            print(f'Records exist. There are {len(messages)} records to process.')
            for message in messages:
                buffer.append(message.value)
            # print(message.value)

        now = datetime.utcnow()
        if (now - last_write_time) >= timedelta(minutes=5):
            if buffer:
                df = pd.DataFrame(buffer)
                # df.to_csv('test_data.csv', index=False)
                parquet_buffer = BytesIO()
                df.to_parquet(parquet_buffer, index=False)

                s3_path = f"{now.year}/{now.month:02}/{now.day:02}/weather_{now.strftime('%H%M%S')}.parquet"

                print(f"Uploading {len(buffer)} records to s3://{S3_BUCKET}/{s3_path}")
                upload_fileobj(S3_BUCKET, s3_path, parquet_buffer)

                buffer.clear()
                last_write_time = now

        # Small sleep to reduce CPU when no messages
        time.sleep(1)

except Exception as e:
    print(f"[Consumer] Unexpected error: {e}")

finally:
    print("[Consumer] Shutting down...")

    # Final S3 upload of any remaining buffer
    if buffer:
        print(f"[Consumer] Uploading remaining {len(buffer)} records before shutdown...")
        df = pd.DataFrame(buffer)
        # df.to_csv('test_data.csv', index=False, mode='a')
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)

        now = datetime.utcnow()
        s3_path = f"{now.year}/{now.month:02}/{now.day:02}/weather_{now.strftime('%H%M%S')}_final.parquet"
        upload_fileobj(S3_BUCKET, s3_path, parquet_buffer)

    # Close the Kafka connection
    consumer.close()
    print("[Consumer] Shutdown complete.")
