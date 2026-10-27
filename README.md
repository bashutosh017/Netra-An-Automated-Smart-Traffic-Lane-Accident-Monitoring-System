# Netra

**Automated Smart Traffic Lane & Accident Monitoring System**

Netra analyzes uploaded videos and CCTV streams to detect and track vehicles, monitor lane rules, and raise alerts for violations and possible accidents. Alerts are stored in PostgreSQL and shown on a live dashboard.

> **Status:** In development. See the [Roadmap](#roadmap) for what is built and what is planned.

---

## Features

| Feature | Description |
| --- | --- |
| Vehicle detection | Detects cars, buses, trucks, and motorcycles using YOLO |
| Vehicle tracking | Gives each vehicle a persistent ID across frames (ByteTrack) |
| Vehicle counting | Counts vehicles crossing a virtual line without double counting |
| Lane mapping | Uses Canny edges and Hough lines to suggest lane boundaries, then uses configured lane regions |
| Wrong-way detection | Compares each vehicle's direction with the allowed direction of its lane |
| Lane violation detection | Flags vehicles crossing solid lane boundaries |
| Alert storage | Saves alerts with type, severity, timestamp, and evidence snapshot |
| Live dashboard | Shows processed video, counters, charts, and incoming alerts in real time |
| Speed estimation *(planned)* | Calibrated pixel-to-meter conversion |
| Gridlock detection *(planned)* | Vehicle density, low speed, and queue duration |
| Accident detection *(planned)* | Multiple visual signals with temporal checks to reduce false alarms |

---

## How It Works

```
Video (upload or CCTV)
        |
        v
  Read frames            OpenCV
        |
        v
  Detect + track         YOLO + ByteTrack
        |
        v
  Apply lane rules       Lane polygons, direction, boundaries
        |
        v
  Create alert  -->  PostgreSQL  (permanent record)
        |
        +-------->  WebSocket    (live push to dashboard)
        |
        +-------->  Evidence snapshot saved to disk
```

Detection tells Netra what and where, tracking tells it which vehicle over time, and rules decide whether something is a problem.

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Detection and tracking | `ultralytics` (YOLO), `torch`, `torchvision` |
| Video and image processing | `opencv-python`, `numpy` |
| Geometry and filtering *(optional)* | `shapely`, `scipy` |
| Backend API | `fastapi`, `uvicorn`, `python-multipart`, `websockets` |
| Database | PostgreSQL, `sqlalchemy`, `psycopg[binary]`, `alembic` |
| Validation | `pydantic` |
| Frontend | React, Vite, `axios`, `recharts`, `lucide-react` |

---

## Project Structure

```
netra/
├── backend/
│   ├── main.py                    # App entry point, routes, WebSocket
│   ├── config.py                  # Settings (paths, thresholds, database URL)
│   ├── schemas.py                 # Request/response shapes (Pydantic)
│   ├── pipeline.py                # Per-frame loop that coordinates detection modules
│   ├── api/
│   │   ├── videos.py              # Upload, job status, processed video
│   │   └── alerts.py              # List/filter alerts, live alert stream
│   ├── detection/
│   │   ├── vehicle_detector.py    # YOLO detection + tracking IDs
│   │   ├── vehicle_tracker.py     # Position history per vehicle
│   │   ├── lane_detector.py       # Lane suggestions and lane configuration
│   │   ├── violation_detector.py  # Counting, wrong-way, lane crossing
│   │   ├── speed_estimator.py     # Calibrated speed (planned)
│   │   └── accident_detector.py   # Accident candidates (planned)
│   ├── database/
│   │   ├── models.py              # Table definitions
│   │   └── session.py             # Database connection and sessions
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/            # Reusable UI pieces
│       ├── pages/                 # Dashboard, upload, alerts, analytics
│       └── services/              # API client and WebSocket client
├── models/                        # YOLO weight files
├── uploads/                       # Raw uploaded videos
├── processed_videos/              # Annotated videos and evidence snapshots
└── README.md
```

For a file-by-file explanation and pseudocode, see `netra_file_guide_and_pseudocode.md`.

---

## Getting Started

### Prerequisites

- Python 3.11 (check compatibility with your chosen PyTorch build)
- Node.js (for the dashboard)
- PostgreSQL
- Optional: an NVIDIA GPU with a matching CUDA version

### 1. Backend setup

Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Install the packages:

```bash
python -m pip install --upgrade pip

pip install ultralytics opencv-python numpy
pip install fastapi uvicorn python-multipart
pip install sqlalchemy "psycopg[binary]" pydantic alembic
pip install websockets shapely scipy
```

For GPU use, install the PyTorch build that matches your CUDA version by following the [official PyTorch guide](https://pytorch.org/get-started/locally/). Ultralytics also documents its [installation options](https://docs.ultralytics.com/quickstart).

Once your `requirements.txt` is ready, you can install everything at once with `pip install -r backend/requirements.txt`.

### 2. Database setup

1. Create a PostgreSQL database (for example, named `netra`).
2. Put your connection URL in your settings (`config.py` or an environment variable), for example:

   ```
   DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/netra
   ```

3. Create the tables, either by running Alembic migrations or by creating them on application startup.

### 3. Run the backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

FastAPI's interactive API docs will be available at `http://localhost:8000/docs`.

### 4. Frontend setup

```bash
npm create vite@latest netra-frontend -- --template react
cd netra-frontend
npm install
npm install axios recharts lucide-react
npm run dev
```

If you keep the frontend in the `frontend/` folder instead, run the same install and start commands there.

---

## Database: Alerts Table

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | `BIGSERIAL` | Unique alert ID |
| `camera_id` | `VARCHAR(100)` | Source camera |
| `vehicle_type` | `VARCHAR(50)` | Car, bus, truck, motorcycle, etc. |
| `timestamp` | `TIMESTAMPTZ` | Time of the event |
| `infraction_type` | `VARCHAR(100)` | Wrong-way, lane violation, accident, gridlock |
| `infraction_severity` | `VARCHAR(20)` | `Warning` or `Critical` (enforced by a constraint) |
| `vehicle_track_id` | `INTEGER` | Tracker ID for the vehicle |
| `confidence` | `REAL` | Model confidence, where applicable |
| `evidence_path` | `TEXT` | Path to the saved snapshot or clip |

Indexes are recommended on `timestamp`, `camera_id`, and `infraction_type`. Video files are stored on disk; only their paths go in the database.

---

## Roadmap

Build in this order and test each step before moving on.

- [ ] 1. Detect vehicles in a video and draw boxes
- [ ] 2. Add tracking with persistent IDs
- [ ] 3. Count vehicles at a virtual line
- [ ] 4. Define lane regions and boundaries
- [ ] 5. Wrong-way and lane-crossing detection
- [ ] 6. Save alerts and evidence to PostgreSQL
- [ ] 7. Wrap the pipeline in a FastAPI service
- [ ] 8. Build the live dashboard
- [ ] 9. Speed estimation and gridlock detection
- [ ] 10. Accident candidate detection and validation

---

## Known Limitations

- Canny and Hough lines only suggest candidate lane lines. Shadows, curves, worn paint, and camera perspective can fool them, so final lanes should be configured per camera.
- Speed in km/h needs per-camera calibration (image points matched to measured real-world distances).
- A stopped vehicle is not proof of an accident. Accident alerts should combine several signals and persist over time.
- Detection settings such as the confidence threshold need tuning for day, night, and rain footage.

---

## Configuration Notes

| Setting | What it controls | Starting point |
| --- | --- | --- |
| `MIN_CONFIDENCE` | Minimum YOLO confidence to keep a detection | 0.4 to 0.5 (lower it if tracking IDs flicker) |
| `ALLOWED_CLASSES` | Which COCO classes count as vehicles | car, motorcycle, bus, truck |
| `MAX_HISTORY` | Positions remembered per vehicle | 30 |
| `FRAME_SKIP` | Process every Nth frame to save time | 1 (no skipping) |
| Alert cooldown | Time before the same alert type repeats for a vehicle | Tune per camera |

---

## License

Add your project license here.

**Important:** Ultralytics YOLO is available under AGPL-3.0 and an Enterprise license. Review the terms before any commercial deployment.

---

## Author

Ashutosh Biswal
mail me: bashutosh017@gmail.com#   N e t r a - A - A u t o m a t e d - S m a r t - T r a f f i c - L a n e - A c c i d e n t - M o n i t o r i n g - S y s t e m  
 