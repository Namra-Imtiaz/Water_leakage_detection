"""
DUMMY DATA SIMULATOR - Replaces ESP32 temporarily.

Two modes (set via DUMMY_MODE env var):
  predict  (default) — generates synthetic ADC samples, POSTs to /api/predict,
                        and lets the backend ML model classify them. Exercises
                        the full pipeline end-to-end.
  legacy             — bypasses the model, POSTs pre-computed labels to
                        /api/leak-data (old behaviour, useful for fast UI testing).

REMOVE or STOP this script once real ESP32 devices are connected.
"""

import os
import random
import time
import numpy as np
import requests
from datetime import datetime

BASE_URL  = os.environ.get("LEAK_API_BASE", "http://127.0.0.1:5000")
SENSOR_ID = 1
SR        = 8000   # must match model training config


# ── Signal generators ─────────────────────────────────────────────────────

def _make_no_leak_signal(seconds: int = 5) -> list:
    """Low-amplitude Gaussian noise — typical quiet pipe."""
    samples = int(SR * seconds)
    adc = np.random.normal(loc=512, scale=8, size=samples).clip(0, 1023)
    return adc.astype(int).tolist()


def _make_leak_signal(seconds: int = 5) -> list:
    """
    Burst noise with 50-200 Hz sinusoidal component — mimics leak acoustic emission.
    Reference: Hunaidi & Chu 1999; Cheng & Shen 2022.
    """
    samples = int(SR * seconds)
    t     = np.linspace(0, seconds, samples)
    freq  = random.uniform(50, 200)
    sine  = np.sin(2 * np.pi * freq * t) * random.uniform(40, 80)
    noise = np.random.normal(0, 12, samples)
    adc   = (512 + sine + noise).clip(0, 1023)
    return adc.astype(int).tolist()


# ── Senders ───────────────────────────────────────────────────────────────

def send_predict(is_leak: bool) -> None:
    """POST raw ADC samples to /api/predict — backend runs ML inference."""
    adc_values = _make_leak_signal() if is_leak else _make_no_leak_signal()
    payload = {
        "sensor_id": SENSOR_ID,
        "adc_values": adc_values,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    try:
        r = requests.post(f"{BASE_URL}/api/predict", json=payload, timeout=30)
        if r.status_code in (200, 201):
            resp = r.json()
            print(
                f"[predict] sent={'leak' if is_leak else 'no_leak'} | "
                f"model={resp['leak_status']} ({resp['confidence']:.2f}) | "
                f"windows={resp['windows_processed']} | event_id={resp['event_id']}"
            )
        else:
            print(f"[predict] Error {r.status_code}: {r.text}")
    except requests.exceptions.ConnectionError:
        print("[predict] Backend not running — start Flask first: python app.py")
    except Exception as e:
        print(f"[predict] Error: {e}")


def send_legacy() -> None:
    """POST pre-computed label to /api/leak-data (bypasses ML model)."""
    is_leak     = random.random() < 0.15
    leak_status = "Leak" if is_leak else "No Leak"
    confidence  = round(random.uniform(0.75, 0.99), 2)
    payload = {
        "sensor_id": SENSOR_ID,
        "leak_status": leak_status,
        "confidence": confidence,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    try:
        r = requests.post(f"{BASE_URL}/api/leak-data", json=payload, timeout=5)
        if r.status_code in (200, 201):
            print(f"[legacy] Sent: {payload}")
        else:
            print(f"[legacy] Error {r.status_code}: {r.text}")
    except requests.exceptions.ConnectionError:
        print("[legacy] Backend not running — start Flask first: python app.py")
    except Exception as e:
        print(f"[legacy] Error: {e}")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    mode     = os.environ.get("DUMMY_MODE", "predict").lower()
    interval = int(os.environ.get("DUMMY_INTERVAL", 10))

    print(f"Dummy sender started — mode={mode}, interval={interval}s. Stop with Ctrl+C.")
    print(f"Backend: {BASE_URL}")

    if mode not in ("predict", "legacy"):
        print(f"Unknown DUMMY_MODE '{mode}'. Use 'predict' or 'legacy'.")
        return

    while True:
        if mode == "predict":
            send_predict(is_leak=random.random() < 0.15)
        else:
            send_legacy()
        time.sleep(interval)


if __name__ == "__main__":
    main()
