"""
ML inference for water leak detection.
Replicates the exact preprocessing pipeline from the training notebook (v2):
  raw ADC  →  50%-overlap 1-second windows at 8kHz
           →  64×64 mel spectrogram + delta + delta²  (3-channel)
           →  teacher model (input shape 64×64×3)
           →  sigmoid probability
"""

import os
import numpy as np
import librosa
import cv2
import tensorflow as tf

# ── Constants (must match training config exactly) ─────────────────────────
SR          = 8000
WIN_SAMPLES = int(SR * 1.0)       # 1-second window = 8000 samples
HOP_STEP    = WIN_SAMPLES // 2    # 50% overlap → more windows per signal
N_FFT       = 512
HOP_LENGTH  = 128
N_MELS      = 64
F_MIN       = 50
F_MAX       = 1800                # ← CHANGED from 3800 to 1800
TARGET_SIZE = (64, 64)            # teacher input spatial size

# ── Threshold ──────────────────────────────────────────────────────────────
# Optimal threshold found via find_optimal_threshold() on the validation set
# (maximises balanced accuracy). Source: STEP 8 training output.
# "Optimal threshold: 0.65  (val Balanced Acc=0.7117)"
THRESHOLD   = 0.65

MODEL_PATH  = os.path.join(os.path.dirname(__file__), "teacher_best.keras")

_model = None


def _load_model():
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(MODEL_PATH)
    return _model


def _make_mel(window: np.ndarray) -> np.ndarray:
    """
    Convert a 1-second float32 signal window into a normalised 64×64×3 array.

    Channel 0: mel spectrogram (dB)
    Channel 1: first-order delta (temporal derivative)
    Channel 2: second-order delta (acceleration)

    Matches training pipeline exactly (v2 notebook, STEP 3).
    """
    # ── Base mel spectrogram ───────────────────────────────────────────────
    S    = librosa.feature.melspectrogram(
               y=window, sr=SR, n_fft=N_FFT, hop_length=HOP_LENGTH,
               n_mels=N_MELS, fmin=F_MIN, fmax=F_MAX)
    S_db = librosa.power_to_db(S, ref=np.max)

    # ── Temporal deltas ────────────────────────────────────────────────────
    delta  = librosa.feature.delta(S_db)
    delta2 = librosa.feature.delta(S_db, order=2)

    # ── Resize all three channels to TARGET_SIZE ───────────────────────────
    spec   = cv2.resize(S_db,    TARGET_SIZE, interpolation=cv2.INTER_LINEAR)
    spec_d = cv2.resize(delta,   TARGET_SIZE, interpolation=cv2.INTER_LINEAR)
    spec_d2= cv2.resize(delta2,  TARGET_SIZE, interpolation=cv2.INTER_LINEAR)

    # ── Stack into (64, 64, 3) ─────────────────────────────────────────────
    stacked = np.stack([spec, spec_d, spec_d2], axis=-1).astype(np.float32)

    # ── Per-sample standardisation on the full 3-channel array ────────────
    stacked = (stacked - stacked.mean()) / (stacked.std() + 1e-9)
    return stacked   # shape: (64, 64, 3)


def _load_signal_from_csv(path: str) -> np.ndarray:
    """
    Load raw ADC signal from a CSV file.
    Expected format: header row, then rows of (time, adc_value).
    Returns normalised float32 array centred at 0, range [-1, 1].
    """
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    adc  = data[:, 1].astype(np.float32)
    adc  = np.nan_to_num(adc)
    # return (adc - 512.0) / 512.0
    return (adc - 2048.0) / 2048.0


def predict_from_signal(signal: np.ndarray, threshold: float = THRESHOLD) -> dict:
    """
    Run leak prediction on a raw ADC signal array.

    Uses 50% overlapping 1-second windows (matches v2 training pipeline).
    Aggregates across windows by taking the MAX confidence — conservative
    strategy: flag a leak if ANY window detects one.

    Args:
        signal:    Normalised float32 array (values in [-1, 1]).
        threshold: Decision boundary (default 0.5; use optimal from training).

    Returns:
        {
          "leak_status":       "Leak" | "No Leak",
          "confidence":        float (0–1),
          "windows_processed": int
        }
    """
    model = _load_model()

    # ── Build 3-channel spectrogram for each 50%-overlapping window ────────
    specs = []
    for start in range(0, len(signal) - WIN_SAMPLES + 1, HOP_STEP):
        window = signal[start:start + WIN_SAMPLES]
        specs.append(_make_mel(window))          # each: (64, 64, 3)

    if not specs:
        raise ValueError(
            "Signal too short — need at least 8000 samples (1 second at 8kHz)"
        )

    X = np.array(specs, dtype=np.float32)        # shape: (N, 64, 64, 3)
    probs = model.predict(X, verbose=0).flatten()  # shape: (N,)

    # Aggregate: max probability across all windows
    confidence  = float(np.max(probs))
    leak_status = "Leak" if confidence >= threshold else "No Leak"

    return {
        "leak_status":       leak_status,
        "confidence":        round(confidence, 4),
        "windows_processed": len(specs),
    }


def predict_from_csv(path: str, threshold: float = THRESHOLD) -> dict:
    """Load a CSV file and run predict_from_signal on it."""
    signal = _load_signal_from_csv(path)
    return predict_from_signal(signal, threshold=threshold)


def predict_from_raw_adc(adc_values: list, threshold: float = THRESHOLD) -> dict:
    """Run prediction on a list of raw ADC integer values (0-4095, 12-bit ESP32 ADC)."""
    '''Normalises to [-1, 1] before inference (matches training load_signal()).'''

    adc    = np.array(adc_values, dtype=np.float32)
    adc    = np.nan_to_num(adc)
    #signal = (adc - 512.0) / 512.0
    signal = (adc - 2048.0) / 2048.0
    return predict_from_signal(signal, threshold=threshold)
