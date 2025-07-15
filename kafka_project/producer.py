import requests
import time
import json
import signal
import sys
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('api_key')
BASE_URL = "https://api.weatherapi.com/v1/current.json"

# Set up Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

running = True
def signal_handler(sig, frame):
    '''Gracefully shutdown function if this script terminates'''
    global running
    print("\n[Producer] Shutdown signal received. Exiting loop gracefully...")
    running = False

# Register the signal handler for Ctrl+C (SIGINT) and termination (SIGTERM)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def frange(start, stop, step):
    '''Create range of values'''
    while start <= stop:
        yield round(start, 2)
        start += step

try:
    while running:
        start_time = time.time()
        print("Starting new grid scan...")
        for lat in frange(49.0, 50.0, 0.1):
            for lon in frange(-123.0, -122.0, 0.1):
                if not running:
                    print("[Producer] Breaking out of grid scan loop.")
                    break
                # Send API request with latitude and longitude as queries
                params = {"key": API_KEY, "q": f"{lat},{lon}", "aqi": "yes"}
                try:
                    response = requests.get(BASE_URL, params=params, timeout=10)
                    response.raise_for_status()
                    # Obtain data from API
                    weather_data = response.json()

                    # Format weather data
                    message = {
                        "latitude": lat,
                        "longitude": lon,
                        "local_time": weather_data['location']['localtime'],
                        "updated_time": weather_data['current']['last_updated'],
                        "temp_celsius": weather_data['current']['temp_c'],
                        "wind_speed_kph": weather_data['current']['wind_kph'],
                        "pressure_mb": weather_data['current']['pressure_mb'],
                        "precipitation_mm": weather_data['current']['precip_mm'],
                        "humidity": weather_data['current']['humidity'],
                        "cloud_cover": weather_data['current']['cloud'],
                        "uv_index": weather_data['current']['uv'],
                    }
                    # Send weather data to Kafka topic
                    producer.send("weather-data", message)
                    print(f"Sent weather for {lat}, {lon}")

                except Exception as e:
                    print(f"Error at {lat},{lon}: {e}")
                
                time.sleep(0.5)

        if running:
            # Ensure that we are collecting data once every 5 minutes exactly
            end_time = time.time()
            elapsed_time = end_time - start_time
            sleep_time = max(0, 300 - elapsed_time)

            print(f"Completed grid scan in {elapsed_time:.2f} seconds. Sleeping for {sleep_time:.2f} seconds to run every 5 minutes.")
            for _ in range(int(sleep_time)):  # Sleep in small increments so we can exit during sleep
                if not running:
                    break
                time.sleep(1)

except Exception as e:
    print(f"[Producer] Unexpected error: {e}")

finally:
    # Closing Kafka Producer when script terminates
    print("[Producer] Flushing and closing producer...")
    producer.flush()
    producer.close()
    print("[Producer] Shutdown complete.")
