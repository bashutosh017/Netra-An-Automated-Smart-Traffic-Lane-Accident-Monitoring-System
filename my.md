# Netra: Required Libraries and Tech Stack

For Netra — Automated Smart Traffic Lane & Accident Monitoring System, I recommend a Python-based computer vision stack with YOLO + OpenCV + FastAPI + PostgreSQL. This combination supports video processing, vehicle detection and tracking, lane-violation monitoring, accident alerts, and a real-time dashboard.

The key is to keep the first version manageable: detect vehicles, map lane boundaries, track movement, and log violations before adding more advanced features such as speed estimation and gridlock detection.

## 1. Recommended technology stack

Optimize Traffic with YOLO11 | Ultralytics

AI and vehicle detection

`ultralytics`, `torch`, `torchvision`

Detect cars, buses, trucks, motorcycles, and other supported vehicle classes. YOLO provides the object-detection model; PyTorch runs the model.

Alternatives and detailed information of Opencv Lane Vehicle Track - GitPlanet

Lane detection and video processing

`opencv-python`, `numpy`

Decode uploaded videos or CCTV streams, apply Canny edge detection and Hough line transforms, draw virtual lane boundaries, and annotate processed frames.

Dependencies - FastAPI

Backend and API

`fastapi`, `uvicorn`, `python-multipart`

Accept video uploads, expose detection results, manage processing jobs, and deliver traffic alerts to the dashboard.

PostgreSQL Logo PNG Transparent & SVG Vector - Freebie Supply

Database and data validation

`sqlalchemy`, `psycopg`, `alembic`, `pydantic`

Store alerts, vehicle types, timestamps, severity, camera information, and detection metadata.

Sri Gokul Krishnan - Traffic Monitoring / Dashboard Design

Frontend dashboard

`react`, `vite`, `axios`, `recharts`

Display annotated video, vehicle counts, traffic conditions, alert tables, and analytics charts. Use WebSockets for live updates.

## 2. Essential Python libraries

These are the main packages I would install for the backend and AI pipeline.

| Library | Required? | Purpose |
| --- | --- | --- |
| `ultralytics` | Essential | YOLO vehicle detection and tracking |
| `opencv-python` | Essential | Video decoding, Canny edges, Hough lines, frame annotation |
| `numpy` | Essential | Image arrays, geometry, coordinates, speed calculations |
| `torch` | Essential | Deep learning inference through PyTorch |
| `fastapi` | Essential | REST API and backend endpoints |
| `uvicorn` | Essential | Runs the FastAPI server |
| `python-multipart` | Essential | Handles uploaded video files |
| `sqlalchemy` | Essential | Database models and queries |
| `psycopg[binary]` | Essential | PostgreSQL database driver |
| `pydantic` | Essential | Validate API requests and responses |
| `alembic` | Recommended | Database schema migrations |
| `websockets` | Recommended | WebSocket support for live dashboard updates |

YOLO's tracking mode supports video and stream inputs and can maintain vehicle identities across consecutive frames, which is important for counting vehicles and detecting lane crossings.

GitHub

+1

## 3. Additional libraries for Netra's specific features

Lane boundary and lane violation detection

- `cv2.Canny()` — detect road edges.
- `cv2.HoughLinesP()` — identify candidate lane lines.
- `shapely` — optional, for geometric lane polygons and boundary intersections.
- `numpy` — calculate vehicle positions relative to lane boundaries.

Note: Canny and Hough lines find candidate edges and lines; perspective, shadows, curves, and road markings may require additional calibration or lane segmentation.

Vehicle counting and wrong-way driving

- `ultralytics` — detect and track vehicles.
- Built-in YOLO tracking with ByteTrack — associate detections across frames.
- `collections.deque` — retain recent positions and movement history.

Compare the vehicle's direction of travel against the configured permitted direction for each lane.

Speed estimation and gridlock

- `numpy` — calculate movement and displacement.
- `scipy` — optional for smoothing and filtering measurements.
- `opencv-python` — perspective transformation and camera calibration.

Speed in km/h requires a calibrated relationship between image coordinates and real-world distance. Gridlock detection can use vehicle density, movement, and queue duration.

Accident and incident monitoring

- `ultralytics` — vehicle detection and tracking.
- `opencv-python` — detect stopped vehicles and analyze changes across frames.
- Optional: a custom-trained accident-classification model or a video-action-recognition model.

A stopped vehicle alone is not proof of an accident. Use multiple visual signals and temporal checks to reduce false alarms.

## 4. Installation commands

Create a Python virtual environment first. Python 3.11 is a reasonable starting point, subject to the compatibility requirements of your selected PyTorch build.

bash

```
python -m venv .venv
```

Activate it:

bash

```
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Install the core AI and backend packages:

bash

```
python -m pip install --upgrade pip

pip install ultralytics opencv-python numpy
pip install fastapi uvicorn python-multipart
pip install sqlalchemy "psycopg[binary]" pydantic alembic
pip install websockets shapely scipy
```

PyTorch is a dependency of the YOLO stack, but for a GPU setup, install the appropriate PyTorch build for your CUDA version by following the [official PyTorch installation guide](<https://pytorch.org/get-started/locally/?utm_source=chatgpt.com>). Ultralytics also documents its [installation options](<https://docs.ultralytics.com/quickstart?utm_source=chatgpt.com>).

Ultralytics Docs

+1

### Frontend installation

If you choose React for the dashboard, install Node.js and then run:

bash

```
npm create vite@latest netra-frontend -- --template react
cd netra-frontend
npm install
npm install axios recharts lucide-react
```

Recommended frontend packages:

- `react` and `vite` — interface and development tooling.
- `axios` — API requests.
- `recharts` — vehicle counts and traffic analytics.
- `lucide-react` — dashboard icons.
- Native `WebSocket` API — real-time alerts without an additional WebSocket client library.

## 5. Suggested project structure

text

```
netra/
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── videos.py
│   │   └── alerts.py
│   ├── detection/
│   │   ├── vehicle_detector.py
│   │   ├── vehicle_tracker.py
│   │   ├── lane_detector.py
│   │   ├── violation_detector.py
│   │   ├── speed_estimator.py
│   │   └── accident_detector.py
│   ├── database/
│   │   ├── models.py
│   │   └── session.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
├── models/
├── uploads/
├── processed_videos/
└── README.md
```

## 6. PostgreSQL alert schema

Your alert table should support the fields you described, along with a few additional fields for traceability.

| Column | Suggested type | Purpose |
| --- | --- | --- |
| `id` | `BIGSERIAL` | Unique alert ID |
| `camera_id` | `VARCHAR(100)` | Source camera |
| `vehicle_type` | `VARCHAR(50)` | Car, bus, truck, motorcycle, etc. |
| `timestamp` | `TIMESTAMPTZ` | Time of the event |
| `infraction_type` | `VARCHAR(100)` | Wrong-way, lane violation, accident, gridlock |
| `infraction_severity` | `VARCHAR(20)` | Warning or Critical |
| `vehicle_track_id` | `INTEGER` | Tracker ID for the vehicle |
| `confidence` | `REAL` | Model confidence, where applicable |
| `evidence_path` | `TEXT` | Saved snapshot or evidence clip path |

Use PostgreSQL constraints for severity values and indexes on timestamps, camera IDs, and event types. Store large video files separately rather than directly in the alert table.

## 7. What to implement first

1. Vehicle detection: Load a pretrained YOLO model and detect vehicles in an uploaded video.
2. Tracking and counting: Assign persistent vehicle IDs and count vehicles without double-counting them.
3. Lane mapping: Use Canny edge detection and Hough line transforms to identify candidate lane boundaries, then configure virtual lane regions.
4. Violation detection: Check vehicle trajectories against permitted lane directions and boundaries.
5. Alert storage: Save detected events to PostgreSQL with timestamps, severity, and evidence.
6. Live dashboard: Display the processed video, counters, and incoming alerts.
7. Advanced features: Add calibrated speed estimation, gridlock analysis, and a separately validated accident-detection model.

My final recommendation: Start with YOLO + OpenCV + NumPy + FastAPI + SQLAlchemy + PostgreSQL + React. Add the other libraries only when the corresponding feature is implemented. This is sufficient for a strong initial prototype.

One important production consideration: the Ultralytics licensing terms distinguish between AGPL-3.0 and Enterprise licensing, so review them before commercial deployment.

Ultralytics