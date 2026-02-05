# Water Leakage Detection and Monitoring System (LeakSense)

Full-stack Final Year Project: **Flask (Python) backend + SQLite + React frontend**.  
Monitors water pipelines using sensor nodes; currently uses **dummy data** to simulate ESP32. When ready, ESP32 + TensorFlow Lite will POST the same JSON to the backend—**no backend changes required**.

---

## Tech Stack

- **Backend:** Python Flask  
- **Database:** SQLite (built into Python)  
- **Frontend:** React (Vite)  
- **APIs:** REST, JSON  
- **No Node.js backend** (React talks to Flask only)

---

## SQLite — You Don’t Need to Install It

**SQLite is included with Python.** There is no separate “SQLite server” to install.

1. **Check Python:**  
   `python --version` or `python3 --version` (3.8+ recommended).

2. **SQLite module:**  
   Python’s standard library includes `sqlite3`. No `pip install` for SQLite.

3. **What the project does:**  
   - On first run, the app creates a file `backend/database.db`.  
   - All data is stored in that single file.  
   - No database server process; no username/password.

4. **Optional: SQLite CLI (for inspection):**  
   - **Windows:** Download from [sqlite.org/download](https://www.sqlite.org/download.html) (e.g. “Precompiled Binaries for Windows” → `sqlite-tools-*.zip`). Extract and add the folder to PATH.  
   - **macOS:** Often pre-installed; or `brew install sqlite`.  
   - **Linux:** `sudo apt install sqlite3` (Ubuntu/Debian) or equivalent.  
   Then: `cd backend` and run `sqlite3 database.db` to run SQL.

**Summary:** Install Python, run the backend as below; the app will create and use `database.db` automatically. The optional CLI is only if you want to inspect the database manually.

---

## Project Structure

```
backend/
  app.py              # Flask app entry
  init_db.py          # Create DB and tables (run once)
  database.db         # Created automatically (SQLite file)
  requirements.txt
  dummy_sender.py     # Simulates ESP32 (remove when ESP32 is connected)
  models/
    db.py             # DB connection and init
  routes/
    leak_routes.py    # REST API endpoints

frontend/
  src/
    App.jsx
    main.jsx
    services/api.js   # API client
    pages/
      Dashboard.jsx
      Analytics.jsx
    components/
      EventTable.jsx, SensorHealthPanel.jsx, SummaryCards.jsx
      LeakEventsChart.jsx, SummaryChart.jsx, ConfidenceChart.jsx
  package.json
  vite.config.js
```

---

## How to Run

### 1. Backend (Flask + SQLite)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python init_db.py              # Create database and tables (once)
python app.py                  # Start Flask on http://127.0.0.1:5000
```

- **SQLite:** No extra install. Running `init_db.py` or `app.py` creates `backend/database.db` if it doesn’t exist. If you had an older DB with pipe sections, delete `backend/database.db` and run `python init_db.py` again.

### 2. Dummy Data (simulates ESP32)

In a **second terminal** (with the same venv if you use one):

```bash
cd backend
venv\Scripts\activate          # if using venv
pip install requests           # if not already installed
python dummy_sender.py
```

- Sends Leak/No Leak + confidence to `POST /api/leak-data` every few seconds.  
- **Stop when real ESP32 is connected;** the backend API stays the same.

### 3. Frontend (React)

In a **third terminal**:

```bash
cd frontend
npm install
npm run dev
```

- Open **http://localhost:5173**.  
- Vite proxy forwards `/api` to Flask (see `vite.config.js`).

---

## API Summary

| Method | Endpoint           | Purpose                                      |
|--------|--------------------|----------------------------------------------|
| POST   | `/api/leak-data`   | Receive leak result (dummy now, ESP32 later) |
| GET    | `/api/recent-events` | Latest events for dashboard table          |
| GET    | `/api/event-history` | Historical events for charts               |
| GET    | `/api/summary`     | Leak vs No Leak counts                       |
| GET    | `/api/sensor-health` | Sensor status (Active/Inactive, last_seen) |

**POST /api/leak-data** example (single sensor; leak vs no leak only—same format ESP32 will use):

```json
{
  "sensor_id": 1,
  "leak_status": "Leak",
  "confidence": 0.92,
  "timestamp": "2026-01-28 10:30"
}
```

---

## Frontend Overview

- **Dashboard:** Summary cards (Leak/No Leak status, confidence, last event time, sensor health), real-time events table, sensor health panel.  
- **Analytics:** Time-based leak events chart, Leak vs No Leak bar chart, confidence trend chart.

---

## Connecting ESP32 + AI Later (No Backend Change)

1. **ESP32:**  
   - Read vibration sensor, run TensorFlow Lite on device.  
   - Output: `leak_status` (“Leak” / “No Leak”) and `confidence` (0–1).

2. **Send to backend:**  
   - HTTP POST to `http://<your-server>:5000/api/leak-data` with the same JSON as above (add `sensor_id` and `timestamp` on device).

3. **Backend:**  
   - Already validates and stores this JSON. No new endpoints or schema change; just point ESP32 at the same URL and **stop the dummy sender**.

4. **Optional:**  
   - Use WiFi/HTTPS, auth, or API key later; the existing route and DB logic can stay as-is.

---

## License

For educational / Final Year Project use.
