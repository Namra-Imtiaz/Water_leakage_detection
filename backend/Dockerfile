# ── Hugging Face Spaces requires port 7860 ────────────────────────────────
FROM python:3.11-slim

# System deps for librosa (libsndfile) and OpenCV (libGL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    libglib2.0-0 \
    libgl1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy all backend source
COPY . .

# Hugging Face Spaces MUST use port 7860
EXPOSE 7860

# Init DB then start with gunicorn
# --timeout 120  → allows TF model to load on first request
# --workers 1    → single worker keeps RAM predictable (TF is large)
CMD ["sh", "-c", "python init_db.py && gunicorn app:app --bind 0.0.0.0:7860 --workers 1 --timeout 120"]
