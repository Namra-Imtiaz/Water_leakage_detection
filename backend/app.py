"""
Water Leakage Detection and Monitoring System - Flask Backend

System flow: Sensor -> ESP32 (AI) -> Flask API -> SQLite -> React Dashboard
Backend does NOT train AI or process raw vibration data.
It only receives and stores prediction results (Leak/No Leak + confidence).
"""

import os
from flask import Flask
from flask_cors import CORS

from models.db import init_database
from routes.leak_routes import leak_bp

app = Flask(__name__)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Add your Vercel frontend URL below after deployment
CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://leaksense.vercel.app",                          # production
    "https://leaksense-git-main-namra-imtiazs-projects.vercel.app",  # git branch preview
    "https://leaksense-mbzp9fz3i-namra-imtiazs-projects.vercel.app", # deployment preview
])

# Register API blueprint
app.register_blueprint(leak_bp)


@app.route("/")
def index():
    return {"message": "Water Leakage Detection API", "docs": "Use /api/* endpoints"}


@app.route("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Ensure DB exists before running
    init_database()
    # Port: 7860 for Hugging Face Spaces, 5000 for local dev
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

