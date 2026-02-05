"""
REST API routes for leak detection data.
These endpoints are consumed by the React dashboard.
In future: POST /api/leak-data will be called by ESP32 devices.
"""

from flask import Blueprint, request, jsonify
from models.db import get_connection

leak_bp = Blueprint("leak", __name__, url_prefix="/api")


# ---------------------------------------------------------------------------
# POST /api/leak-data
# ---------------------------------------------------------------------------
# PURPOSE: Receives leak detection results (dummy data now, ESP32 later).
# FUTURE: ESP32 will run TensorFlow Lite model locally on device,
#         then POST only prediction results (leak_status + confidence) here.
#         Backend logic will NOT change - same JSON, same validation.
# ---------------------------------------------------------------------------
@leak_bp.route("/leak-data", methods=["POST"])
def receive_leak_data():
    """
    Receive leak detection result from sensor/ESP32.
    Validates JSON and stores in SQLite.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields (single sensor; leak vs no leak only, no pipe sections)
    required = ["sensor_id", "leak_status", "confidence", "timestamp"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    sensor_id = int(data["sensor_id"])
    leak_status = data["leak_status"]
    confidence = float(data["confidence"])
    timestamp = data["timestamp"]

    if leak_status not in ("Leak", "No Leak"):
        return jsonify({"error": "leak_status must be 'Leak' or 'No Leak'"}), 400
    if not (0 <= confidence <= 1):
        return jsonify({"error": "confidence must be between 0 and 1"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO leak_events (sensor_id, leak_status, confidence, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (sensor_id, leak_status, confidence, timestamp),
        )
        conn.commit()
        event_id = cursor.lastrowid

        # Update or insert single sensor health (last_seen, mark as Active)
        cursor.execute(
            """
            INSERT INTO sensors (sensor_id, sensor_name, health_status, last_seen)
            VALUES (?, 'Sensor', 'Active', ?)
            ON CONFLICT(sensor_id) DO UPDATE SET
                health_status = 'Active',
                last_seen = excluded.last_seen
            """,
            (sensor_id, timestamp),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"success": True, "event_id": event_id}), 201


# ---------------------------------------------------------------------------
# GET /api/recent-events
# ---------------------------------------------------------------------------
@leak_bp.route("/recent-events", methods=["GET"])
def get_recent_events():
    """Returns latest leak events for dashboard table."""
    limit = request.args.get("limit", 50, type=int)
    limit = min(max(limit, 1), 200)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT event_id, sensor_id, leak_status, confidence, timestamp
        FROM leak_events
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    events = [
        {
            "event_id": r["event_id"],
            "sensor_id": r["sensor_id"],
            "leak_status": r["leak_status"],
            "confidence": r["confidence"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]
    return jsonify(events)


# ---------------------------------------------------------------------------
# GET /api/event-history
# ---------------------------------------------------------------------------
@leak_bp.route("/event-history", methods=["GET"])
def get_event_history():
    """Returns historical leak events for charts (optional date range)."""
    limit = request.args.get("limit", 500, type=int)
    limit = min(max(limit, 1), 2000)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT event_id, sensor_id, leak_status, confidence, timestamp
        FROM leak_events
        ORDER BY timestamp ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    events = [
        {
            "event_id": r["event_id"],
            "sensor_id": r["sensor_id"],
            "leak_status": r["leak_status"],
            "confidence": r["confidence"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]
    return jsonify(events)


# ---------------------------------------------------------------------------
# GET /api/summary
# ---------------------------------------------------------------------------
@leak_bp.route("/summary", methods=["GET"])
def get_summary():
    """Returns total Leak vs No Leak counts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT leak_status, COUNT(*) as count
        FROM leak_events
        GROUP BY leak_status
        """
    )
    rows = cursor.fetchall()
    conn.close()

    summary = {"Leak": 0, "No Leak": 0}
    for r in rows:
        summary[r["leak_status"]] = r["count"]
    return jsonify(summary)


# ---------------------------------------------------------------------------
# GET /api/sensor-health
# ---------------------------------------------------------------------------
@leak_bp.route("/sensor-health", methods=["GET"])
def get_sensor_health():
    """Returns the single sensor status (Active/Inactive, last seen time). Only one sensor in system."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT sensor_id, sensor_name, health_status, last_seen
        FROM sensors
        WHERE sensor_id = 1
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify([])
    return jsonify([
        {
            "sensor_id": row["sensor_id"],
            "sensor_name": row["sensor_name"],
            "health_status": row["health_status"],
            "last_seen": row["last_seen"],
        }
    ])
