import os
import json
import time
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load .env
load_dotenv()

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
KAFKA_SERVER = os.getenv("KAFKA_SERVER")
FLIGHT_API = os.getenv("FLIGHT_API")

# Validate environment variables
if not all([KAFKA_TOPIC, KAFKA_SERVER, FLIGHT_API]):
    raise ValueError("Missing required environment variables: KAFKA_TOPIC, KAFKA_SERVER, or FLIGHT_API")

print(f"Connecting to Kafka: {KAFKA_SERVER}")
print(f"Topic: {KAFKA_TOPIC}")
print(f"Flight API: {FLIGHT_API}")

# Set up Kafka producer with error handling
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=3,
        acks='all',  # Wait for all replicas to acknowledge
        request_timeout_ms=30000,
        retry_backoff_ms=1000
    )
except Exception as e:
    print(f"Failed to create Kafka producer: {e}")
    exit(1)

def fetch_flight_data():
    try:
        response = requests.get(FLIGHT_API, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()
        return data.get("states", [])
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching flight data: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error fetching flight data: {e}")
        return []

def send_to_kafka(flights):
    sent_count = 0
    for flight in flights:
        try:
            # Handle potential None values and array bounds
            if not flight or len(flight) < 15:
                continue
                
            record = {
                "icao24": flight[0] if flight[0] else None,
                "callsign": flight[1].strip() if flight[1] and flight[1].strip() else None,
                "origin_country": flight[2] if flight[2] else None,
                "longitude": flight[5] if flight[5] is not None else None,
                "latitude": flight[6] if flight[6] is not None else None,
                "baro_altitude": flight[7] if flight[7] is not None else None,
                "velocity": flight[9] if flight[9] is not None else None,
                "true_track": flight[10] if flight[10] is not None else None,
                "vertical_rate": flight[11] if flight[11] is not None else None,
                "geo_altitude": flight[13] if flight[13] is not None else None,
                "squawk": flight[14] if flight[14] else None
            }
            
            # Send with callback for error handling
            future = producer.send(KAFKA_TOPIC, record)
            # Don't block on each send, just count successful ones
            sent_count += 1
            
        except Exception as e:
            print(f"Error processing flight record: {e}")
            continue
    
    # Flush to ensure all messages are sent
    producer.flush()
    print(f"✅ Sent {sent_count} flight records to Kafka topic '{KAFKA_TOPIC}'")

if __name__ == "__main__":
    print("Starting flight data producer...")
    try:
        while True:
            print("Fetching flight data...")
            flight_data = fetch_flight_data()
            if flight_data:
                print(f"Retrieved {len(flight_data)} flights")
                send_to_kafka(flight_data)
            else:
                print("No flight data received")
            
            print(f"Waiting 15 seconds before next fetch...")
            time.sleep(15)
            
    except KeyboardInterrupt:
        print("\nShutting down producer...")
    except Exception as e:
        print(f"Unexpected error in main loop: {e}")
    finally:
        producer.close()
        print("Producer closed")