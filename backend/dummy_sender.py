"""
DUMMY DATA SIMULATOR - Replaces ESP32 temporarily.

This script periodically sends Leak/No Leak + confidence data to the Flask API.
It simulates what the ESP32 will do in future:
  - ESP32 runs TensorFlow Lite locally
  - ESP32 POSTs only prediction results (leak_status, confidence) to /api/leak-data
  - Backend receives same JSON; no change needed when ESP32 is connected

REMOVE or STOP this script once real ESP32 devices are connected.
"""

import requests
import random
import time
import sys
import os

# Backend URL - change if your Flask runs on different host/port
API_URL = os.environ.get("LEAK_API_URL", "http://127.0.0.1:5000/api/leak-data")

# Single sensor only; leak vs no leak detection only (no pipe sections)
SENSOR_ID = 1


def get_dummy_timestamp():
    """Generate a timestamp string for dummy data (local time)."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def send_dummy_event():
    """Send one dummy leak detection result (simulates single ESP32/sensor)."""
    # Mostly "No Leak", occasional "Leak" for demo
    leak_status = "Leak" if random.random() < 0.15 else "No Leak"
    confidence = round(random.uniform(0.75, 0.99), 2)

    payload = {
        "sensor_id": SENSOR_ID,
        "leak_status": leak_status,
        "confidence": confidence,
        "timestamp": get_dummy_timestamp(),
    }
    try:
        r = requests.post(API_URL, json=payload, timeout=5)
        if r.status_code in (200, 201):
            print(f"Sent: {payload}")
        else:
            print(f"Error {r.status_code}: {r.text}")
    except requests.exceptions.ConnectionError:
        print("Backend not running? Start Flask first: python app.py")
    except Exception as e:
        print(f"Error: {e}")


def main():
    print("Dummy sender started (simulates ESP32). Stop with Ctrl+C.")
    print("Backend URL:", API_URL)
    interval = int(os.environ.get("DUMMY_INTERVAL", 5))  # seconds
    while True:
        send_dummy_event()
        time.sleep(interval)


if __name__ == "__main__":
    main()
