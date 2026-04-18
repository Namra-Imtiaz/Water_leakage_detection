"""
ML inference for water leak detection.
Replicates the exact preprocessing pipeline from the training notebook:
  raw ADC CSV  →  1-second windows at 8kHz  →  64×64 mel spectrogram  →  teacher model  →  sigmoid prob
"""

import os
import numpy as np
import librosa
import cv2
import tensorflow as tf

# ── Constants (must match training config) ────────────────────────────────
SR          = 8000
WIN_SAMPLES = int(SR * 1.0)   # 1-second window
N_FFT       = 512
HOP_LENGTH  = 128
N_MELS      = 64
F_MIN       = 50
F_MAX       = 3800
TARGET_SIZE = (64, 64)        # teacher input

THRESHOLD   = 0.5             # default; override with find_optimal_threshold result

MODEL_PATH  = os.path.join(os.path.dirname(__file__), "teacher_best.keras")

_model = None


def _load_model():
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(MODEL_PATH)
    return _model


def _make_mel(window: np.ndarray) -> np.ndarray:
    """Convert a 1-second float32 signal window into a normalised 64×64 mel spectrogram."""
    S    = librosa.feature.melspectrogram(
               y=window, sr=SR, n_fft=N_FFT, hop_length=HOP_LENGTH,
               n_mels=N_MELS, fmin=F_MIN, fmax=F_MAX)
    S_db = librosa.power_to_db(S, ref=np.max)
    spec = cv2.resize(S_db, TARGET_SIZE, interpolation=cv2.INTER_LINEAR)
    spec = spec.astype(np.float32)
    # per-sample standardisation (matches training)
    spec = (spec - spec.mean()) / (spec.std() + 1e-9)
    return spec


def _load_signal_from_csv(path: str) -> np.ndarray:
    """
    Load raw ADC signal from a CSV file.
    Expected format: header row, then rows of (time, adc_value).
    Returns normalised float32 array centred at 0.
    """
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    adc  = data[:, 1].astype(np.float32)
    adc  = np.nan_to_num(adc)
    return (adc - 512.0) / 512.0


def predict_from_signal(signal: np.ndarray, threshold: float = THRESHOLD) -> dict:
    """
    Run leak prediction on a raw ADC signal array.

    Splits signal into non-overlapping 1-second windows, runs each through
    the teacher model, and aggregates by taking the max confidence across windows
    (most conservative: flag a leak if any window detects one).

    Returns:
        {
          "leak_status": "Leak" | "No Leak",
          "confidence": float (0-1),
          "windows_processed": int
        }
    """
    model = _load_model()

    specs = []
    for start in range(0, len(signal) - WIN_SAMPLES + 1, WIN_SAMPLES):
        window = signal[start:start + WIN_SAMPLES]
        specs.append(_make_mel(window))

    if not specs:
        raise ValueError("Signal too short — need at least 8000 samples (1 second at 8kHz)")

    X = np.expand_dims(np.array(specs, dtype=np.float32), axis=-1)  # (N, 64, 64, 1)
    probs = model.predict(X, verbose=0).flatten()                    # (N,)

    # Aggregate: max probability across windows (leak if any window says leak)
    confidence = float(np.max(probs))
    leak_status = "Leak" if confidence >= threshold else "No Leak"

    return {
        "leak_status": leak_status,
        "confidence": round(confidence, 4),
        "windows_processed": len(specs),
    }


def predict_from_csv(path: str, threshold: float = THRESHOLD) -> dict:
    """Load a CSV file and run predict_from_signal on it."""
    signal = _load_signal_from_csv(path)
    return predict_from_signal(signal, threshold=threshold)


def predict_from_raw_adc(adc_values: list, threshold: float = THRESHOLD) -> dict:
    """
    Run prediction on a list of raw ADC integer values (0-1023, as sent by ESP32).
    Normalises to [-1, 1] before inference.
    """
    adc = np.array(adc_values, dtype=np.float32)
    adc = np.nan_to_num(adc)
    signal = (adc - 512.0) / 512.0
    return predict_from_signal(signal, threshold=threshold)
