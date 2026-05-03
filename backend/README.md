---
title: Water Leakage Detection API
emoji: 💧
colorFrom: blue
colorTo: blue
sdk: docker
pinned: false
---

# Water Leakage Detection Backend API

Flask REST API for the Water Leakage Detection and Monitoring System.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/predict` | Run ML inference on raw ADC samples |
| POST | `/api/leak-data` | Receive pre-computed predictions |
| GET | `/api/recent-events` | Latest leak events |
| GET | `/api/event-history` | Historical data for charts |
| GET | `/api/summary` | Leak vs No Leak counts |
| GET | `/api/sensor-health` | Sensor status |
