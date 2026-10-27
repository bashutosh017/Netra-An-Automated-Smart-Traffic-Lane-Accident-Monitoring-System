# Netra: File Guide and Pseudocode

**Netra: Automated Smart Traffic Lane & Accident Monitoring System**

This document has no real code. It explains **what each file is for** and gives **pseudocode** (plain-language logic) so you can understand the thinking before you write anything.

How to use it:

1. Read Section 1 to see the big picture.
2. Read Section 2 to learn what every file does and how files depend on each other.
3. Read Section 3 and try to write each pseudocode block yourself first, then compare.
4. Follow Section 5 to build in the right order.

---

## 1. The Big Picture

Think of Netra as a factory assembly line. A video goes in one end and alerts come out the other.

```
 VIDEO (upload or CCTV)
        |
        v
 [ Read frame ]          <- OpenCV
        |
        v
 [ Detect vehicles ]     <- YOLO (what is in this frame, and where?)
        |
        v
 [ Track vehicles ]      <- ByteTrack (is this the same car as the last frame?)
        |
        v
 [ Understand the road ] <- Lane polygons, boundary lines, allowed direction
        |
        v
 [ Apply rules ]         <- Wrong-way? Lane violation? Stopped? Too slow?
        |
        v
 [ Create alert ]  --->  PostgreSQL (permanent record)
        |
        +-------------->  WebSocket (live push to dashboard)
        |
        +-------------->  Evidence snapshot saved to disk
```

**Core idea:** detection tells you *what and where*, tracking tells you *who over time*, and rules tell you *whether it is a problem*. Each layer does one job.

---

## 2. File-by-File Guide

### 2.1 Project map

```
netra/
├── backend/
│   ├── main.py
│   ├── config.py                  (suggested addition)
│   ├── schemas.py                 (suggested addition)
│   ├── pipeline.py                (suggested addition)
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

The three files marked "suggested addition" are not in your original structure. I added them because the original has no place for (a) settings, (b) request/response shapes, or (c) the code that ties all detection modules together. Without a coordinator file, `main.py` or the API files tend to become messy.

---

### 2.2 Backend: top-level files

| File | What it is for | Takes in | Gives out | Depends on |
| --- | --- | --- | --- | --- |
| `main.py` | The **entry point**. Creates the FastAPI app, connects the API routes, sets up the WebSocket endpoint, and allows the frontend to talk to the backend (CORS). | Nothing (it is the start) | A running server | `api/*`, `database/session.py` |
| `config.py` *(suggested)* | One place for **settings**: file paths, confidence threshold, which vehicle classes count, how many frames to skip, alert cooldown time, database URL. | Environment variables | Settings values | Nothing |
| `schemas.py` *(suggested)* | Defines the **shape of data** moving in and out of the API (Pydantic). Example: what an alert looks like when sent to the dashboard. | Raw data | Validated data | Nothing |
| `pipeline.py` *(suggested)* | The **conductor**. Runs the per-frame loop and calls the detector, tracker, lane logic, violation logic, and alert saving in the right order. | A video path and camera settings | Annotated video + alerts | All files in `detection/` and `database/` |
| `requirements.txt` | List of Python packages to install. | None | None | None |

### 2.3 Backend: `api/` folder (the doors into your system)

| File | What it is for | Typical endpoints (conceptual) |
| --- | --- | --- |
| `videos.py` | Handles everything about **video files**: receiving an upload, starting a processing job, reporting job status, and serving the processed video. | Upload a video, check job status, get processed video |
| `alerts.py` | Handles everything about **alerts**: listing, filtering by type/severity/camera/date, and fetching one alert with its evidence. Also pushes new alerts live over WebSocket. | List alerts, get one alert, live alert stream |

**Rule of thumb:** API files should be thin. They receive a request, call the right function from somewhere else, and return the result. They should *not* contain detection logic.

### 2.4 Backend: `detection/` folder (the brain)

| File | One-sentence job | Input | Output |
| --- | --- | --- | --- |
| `vehicle_detector.py` | Runs YOLO on a frame and returns the vehicles found. | One frame | List of boxes, classes, confidences |
| `vehicle_tracker.py` | Gives each vehicle a **persistent ID** across frames and remembers its recent path. | Detections per frame | Same detections with track IDs + position history |
| `lane_detector.py` | Defines where lanes are. Uses Canny + Hough to *suggest* lane lines, then stores the final lane polygons and boundary lines you configure. | A reference frame, or manual lane points | Lane polygons, boundary lines, allowed direction per lane |
| `violation_detector.py` | Applies **rules** to tracked vehicles: wrong-way, illegal lane crossing, and vehicle counting. | Tracked vehicles + lane info | List of violation events |
| `speed_estimator.py` | Converts pixel movement into real-world speed using a calibrated mapping. Also helps with gridlock. | Position history + calibration points | Speed per vehicle, average speed per lane |
| `accident_detector.py` | Flags possible accidents using several signals combined (stopped vehicle, sudden stop, overlap between vehicles). | Tracked vehicles + speeds | Possible accident events |

### 2.5 Backend: `database/` folder (the memory)

| File | What it is for |
| --- | --- |
| `models.py` | Describes the **tables**: alerts (and optionally cameras and video jobs). Each class here equals one table. |
| `session.py` | Creates the **connection** to PostgreSQL and provides a way for each request to open and close a database session safely. |

### 2.6 Frontend (suggested file ideas)

| Folder | Example files | What they are for |
| --- | --- | --- |
| `pages/` | `Dashboard`, `UploadPage`, `AlertsPage`, `Analytics` | Full screens the user navigates between |
| `components/` | `VideoPlayer`, `VehicleCounter`, `AlertTable`, `SeverityBadge`, `TrafficChart` | Small reusable pieces placed inside pages |
| `services/` | `apiClient`, `alertSocket` | Talk to the backend. `apiClient` makes normal requests. `alertSocket` holds the live WebSocket connection. |

### 2.7 Non-code folders

| Folder / file | What it is for |
| --- | --- |
| `models/` | Stores the YOLO weight file(s) (for example a pretrained model, or one you train later). |
| `uploads/` | Raw videos uploaded by users. Never modified. |
| `processed_videos/` | Output videos with boxes, lanes, and labels drawn on them. Also a good home for evidence snapshots/clips. |
| `README.md` | Explains the project, how to install it, and how to run it. |

### 2.8 Who depends on whom

```
main.py
  ├── api/videos.py ──┐
  ├── api/alerts.py ──┤
  │                   v
  │             pipeline.py
  │                   │
  │      ┌────────────┼──────────────┬────────────────┬──────────────┐
  │      v            v              v                v              v
  │ vehicle_      vehicle_       lane_detector   violation_     accident_
  │ detector      tracker                         detector       detector
  │                                                  │              │
  │                                           speed_estimator ──────┘
  │
  └── database/session.py ── database/models.py
```

Read it as: *API calls pipeline, pipeline calls detection modules, results are saved by database files.*

---

## 3. Pseudocode

Conventions used below: `FUNCTION`, `IF`, `FOR EACH`, `WHILE`, `RETURN`. Words in CAPITALS are logic keywords. Anything after `//` is a comment.

---

### 3.1 `main.py`: starting the app

```
FUNCTION start_application():
    create web application
    load settings from config

    allow the frontend's address to call this server (CORS)

    attach video routes   (from api/videos)
    attach alert routes   (from api/alerts)
    open a WebSocket route for live alerts

    ON STARTUP:
        connect to the database
        make sure the tables exist (or run migrations)
        load the YOLO model ONCE into memory
            // loading is slow, so never do this per frame or per request

    ON SHUTDOWN:
        close database connection
        release the model
```

**Why this matters:** loading the model once at startup is one of the biggest speed wins in the whole project.

---

### 3.2 `api/videos.py`: handling uploads

```
ENDPOINT upload_video(file, camera_id):
    IF file type is not a supported video format:
        RETURN error "unsupported file"

    IF file size is above the limit:
        RETURN error "file too large"

    save file into uploads/ using a unique name
    create a job record: status = "queued", video path, camera id

    start processing in the BACKGROUND
        // do NOT process inside the request, a long video would time out

    RETURN job id immediately


ENDPOINT get_job_status(job_id):
    find the job in the database
    IF not found: RETURN error "job not found"
    RETURN status, progress percentage, number of alerts so far


ENDPOINT get_processed_video(job_id):
    IF job status is not "done": RETURN error "not ready yet"
    RETURN the file from processed_videos/


BACKGROUND TASK run_job(job_id):
    mark job "processing"
    TRY:
        call pipeline.process_video(video path, camera id)
        mark job "done"
    ON ERROR:
        mark job "failed" and store the error message
```

**Concept to learn:** an API should answer fast. Long work goes to a background task, and the client polls (or is told) when it finishes.

---

### 3.3 `api/alerts.py`: reading and broadcasting alerts

```
ENDPOINT list_alerts(filters, page, page_size):
    start with all alerts
    IF filter camera_id given:      keep only that camera
    IF filter infraction_type:      keep only that type
    IF filter severity:             keep only that severity
    IF filter date_from / date_to:  keep only that time range
    sort newest first
    return only the requested page
    RETURN list + total count


ENDPOINT get_alert(alert_id):
    find alert in database
    IF not found: RETURN error
    RETURN alert details including evidence path


WEBSOCKET live_alerts(connection):
    add connection to the list of connected dashboards
    WHILE connection is open:
        wait (keep alive)
    ON DISCONNECT:
        remove connection from the list


FUNCTION broadcast_alert(alert):
    FOR EACH connected dashboard:
        TRY send alert
        IF sending fails: remove that dashboard from the list
```

---

### 3.4 `detection/vehicle_detector.py`: finding vehicles

```
CONSTANT ALLOWED_CLASSES = car, bus, truck, motorcycle
CONSTANT MIN_CONFIDENCE  = a value you tune (start near 0.4 to 0.5)

FUNCTION detect_and_track(frame):
    results = ask the model to detect AND track objects in this frame
              (tracking keeps IDs from the previous call)

    vehicles = empty list
    FOR EACH object in results:
        IF object class NOT in ALLOWED_CLASSES: skip
        IF object confidence < MIN_CONFIDENCE:  skip
        add to vehicles:
            track_id, class name, box corners, confidence

    RETURN vehicles
```

**Why filter?** YOLO also detects people, traffic lights, bags, and so on. Netra only cares about vehicles.

---

### 3.5 `detection/vehicle_tracker.py`: remembering the past

Detection gives you "a car is here now." Tracking gives you "car #7 was here, then here, then here." Most rules need that history.

```
STATE history = map: track_id -> list of recent (x, y, frame_number)
CONSTANT MAX_HISTORY = number of recent positions to keep (e.g. last 30)

FUNCTION ground_point(box):
    // use the BOTTOM-CENTER of the box, not the middle
    x = (left + right) / 2
    y = bottom
    RETURN (x, y)
    // the bottom is where the tyres touch the road,
    // so it matches the lane on the road surface

FUNCTION update_history(vehicles, frame_number):
    FOR EACH vehicle:
        point = ground_point(vehicle.box)
        append (point, frame_number) to history[vehicle.track_id]
        IF history is longer than MAX_HISTORY:
            remove the oldest entry

    // cleanup, otherwise memory grows forever
    FOR EACH track_id in history:
        IF not seen for many frames:
            delete history[track_id]

FUNCTION get_movement_vector(track_id):
    IF fewer than 2 points stored: RETURN nothing
    oldest = first point
    newest = last point
    RETURN (newest.x - oldest.x, newest.y - oldest.y)

FUNCTION get_displacement(track_id):
    vector = get_movement_vector(track_id)
    RETURN length of vector
```

---

### 3.6 `detection/lane_detector.py`: understanding the road

There are two parts: **suggest** lanes automatically, then **fix** them as configuration. Real roads have shadows, curves, and faded paint, so a fully automatic approach is unreliable. A configured lane map is more trustworthy.

```
// PART A: suggest candidate lane lines (helper tool)
FUNCTION suggest_lane_lines(reference_frame):
    convert frame to grayscale
    blur slightly to remove noise
    find edges (Canny)
    mask out everything except the road area
    find straight line segments in the edges (Hough)
    filter out lines that are too short or have unrealistic angles
    RETURN candidate lines
    // a human looks at these and picks the real ones

// PART B: the lane configuration (the source of truth)
STRUCTURE Lane:
    lane_id
    polygon               // list of corner points covering the lane area
    allowed_direction     // vector, e.g. "moving toward the top of the image"
    left_boundary_type    // "solid" (no crossing) or "dashed" (crossing allowed)
    right_boundary_type

STRUCTURE CountingLine:
    point_a, point_b      // a virtual line across the road

FUNCTION load_lane_config(camera_id):
    read lanes, boundary lines, counting line from config or database
    RETURN them

FUNCTION find_lane_of_point(point, lanes):
    FOR EACH lane:
        IF point is inside lane.polygon:
            RETURN lane
    RETURN nothing   // vehicle is off any known lane

FUNCTION draw_lanes(frame, lanes):
    draw each polygon, boundary, and counting line on the frame
```

**Concept to learn, point inside polygon:** draw an imaginary ray from the point to the right. If it crosses the polygon edges an odd number of times, the point is inside. Libraries do this for you, but understanding it helps debugging.

---

### 3.7 `detection/violation_detector.py`: applying the rules

This is where Netra becomes "smart." Each rule below is small and independent.

#### Rule A: Vehicle counting (without double counting)

```
STATE counted_ids = empty set
STATE total_count = 0

FUNCTION check_counting_line(vehicle, previous_point, current_point, line):
    IF vehicle.track_id is in counted_ids: RETURN nothing

    side_before = which side of the line previous_point is on
    side_now    = which side of the line current_point is on

    IF side_before != side_now:
        add vehicle.track_id to counted_ids
        total_count = total_count + 1
        RETURN "counted"
```

**Concept to learn:** the `counted_ids` set is what prevents counting the same car 100 times while it hovers near the line.

#### Rule B: Wrong-way driving

```
CONSTANT MIN_MOVEMENT      = minimum pixels moved before we trust the direction
CONSTANT CONFIRM_FRAMES    = how many checks in a row must be wrong
STATE    wrong_counter     = map: track_id -> number

FUNCTION check_wrong_way(vehicle, lane):
    movement = get_movement_vector(vehicle.track_id)
    IF movement is nothing OR length(movement) < MIN_MOVEMENT:
        RETURN nothing    // car is basically still, direction is meaningless

    // compare directions using a dot product
    alignment = dot_product(movement, lane.allowed_direction)

    IF alignment < 0:
        // moving against the allowed direction
        wrong_counter[track_id] = wrong_counter[track_id] + 1
    ELSE:
        wrong_counter[track_id] = 0    // reset, it was a one-off

    IF wrong_counter[track_id] >= CONFIRM_FRAMES:
        RETURN violation "wrong-way", severity "Critical"
```

**Concept to learn, dot product:**
- Positive result means the two arrows point roughly the same way.
- Zero means they are perpendicular.
- Negative means they point opposite ways.

The **confirm frames** counter protects you from false alarms caused by tracking jitter.

#### Rule C: Illegal lane crossing

```
FUNCTION check_lane_crossing(vehicle, previous_point, current_point, lanes):
    movement_segment = line from previous_point to current_point

    FOR EACH lane:
        FOR EACH boundary of lane:
            IF boundary.type is "solid"
               AND movement_segment intersects boundary:
                RETURN violation "lane violation", severity "Warning"

    RETURN nothing
```

**Alternative approach:** compare `lane_before` and `lane_now`. If the lane changed and the shared boundary is solid, flag it. Try both and see which is more reliable on your video.

#### Combining the rules

```
FUNCTION run_all_rules(vehicles, lanes, counting_line):
    events = empty list

    FOR EACH vehicle in vehicles:
        previous_point, current_point = last two history points
        lane = find_lane_of_point(current_point, lanes)

        add result of check_counting_line  to events if any
        IF lane exists:
            add result of check_wrong_way   to events if any
        add result of check_lane_crossing  to events if any

    RETURN events
```

---

### 3.8 `detection/speed_estimator.py`: pixels to km/h

You cannot get real speed from pixels alone. A car near the camera moves many pixels, and a distant car moves few, even at the same real speed. You need **calibration**.

```
// ONE-TIME SETUP per camera
FUNCTION calibrate(image_points, real_world_points):
    // image_points: 4 corners of a road section, as pixels
    // real_world_points: the same 4 corners in meters (you measure them)
    build a transformation that maps image coordinates -> road coordinates
    save it

// EVERY FRAME
FUNCTION estimate_speed(track_id, fps):
    IF fewer than N points in history: RETURN nothing

    oldest, newest = first and last points in history
    convert both from pixels to road meters using the transformation
    distance_meters = distance between them
    time_seconds    = (newest.frame - oldest.frame) / fps

    speed_mps = distance_meters / time_seconds
    speed_kmh = speed_mps * 3.6

    smooth the value (average with recent speeds)
    RETURN speed_kmh
```

**Gridlock detection (uses speed too):**

```
CONSTANT SLOW_SPEED      = e.g. below 5 km/h
CONSTANT MIN_VEHICLES    = e.g. at least 8 in the lane
CONSTANT MIN_DURATION    = e.g. 30 seconds
STATE    gridlock_since  = map: lane_id -> time or nothing

FUNCTION check_gridlock(lane, vehicles_in_lane, current_time):
    count = number of vehicles in lane
    avg_speed = average speed of those vehicles

    IF count >= MIN_VEHICLES AND avg_speed < SLOW_SPEED:
        IF gridlock_since[lane] is nothing:
            gridlock_since[lane] = current_time     // start the timer
        ELSE IF current_time - gridlock_since[lane] >= MIN_DURATION:
            RETURN event "gridlock", severity "Warning"
    ELSE:
        gridlock_since[lane] = nothing              // traffic moved, reset

    RETURN nothing
```

---

### 3.9 `detection/accident_detector.py`: possible accidents

**Important:** a stopped car is not an accident. It could be a red light, a breakdown, or a parked vehicle. Combine several signals and require them to persist over time.

```
CONSTANT STOP_DISPLACEMENT = very small movement in pixels
CONSTANT STOP_DURATION     = e.g. 10 seconds
CONSTANT OVERLAP_LIMIT     = how much two boxes must overlap to count
CONSTANT SCORE_THRESHOLD   = how many signals needed to raise an alert

STATE stopped_since = map: track_id -> time or nothing

FUNCTION check_accident(vehicles, speeds, current_time):
    possible_events = empty list

    FOR EACH vehicle:
        score = 0

        // Signal 1: the vehicle is stopped
        IF get_displacement(vehicle) < STOP_DISPLACEMENT:
            IF stopped_since[vehicle] is nothing:
                stopped_since[vehicle] = current_time
            IF current_time - stopped_since[vehicle] >= STOP_DURATION:
                score = score + 1
        ELSE:
            stopped_since[vehicle] = nothing

        // Signal 2: it was moving fast, then suddenly stopped
        IF recent speed was high AND current speed is near zero:
            score = score + 1

        // Signal 3: its box overlaps another vehicle's box
        FOR EACH other vehicle:
            IF overlap(vehicle.box, other.box) > OVERLAP_LIMIT:
                score = score + 1

        // Signal 4 (optional): stopped inside a live traffic lane
        //   where other vehicles are moving around it
        IF stopped AND neighbours are moving:
            score = score + 1

        IF score >= SCORE_THRESHOLD:
            add event "accident", severity "Critical", confidence = score / max_score

    RETURN possible_events
```

**Concept to learn, overlap (IoU):** area where two boxes overlap divided by their total combined area. 0 means no overlap, 1 means identical boxes.

**Later upgrade:** a separately trained classifier can confirm a candidate event before it becomes an alert.

---

### 3.10 `database/models.py` and `session.py`

```
// models.py (conceptual table design)
TABLE alerts:
    id                    unique number, auto-increment
    camera_id             text
    vehicle_type          text
    timestamp             date and time WITH timezone
    infraction_type       text  (wrong-way, lane violation, accident, gridlock)
    infraction_severity   text  (only "Warning" or "Critical" allowed)
    vehicle_track_id      integer
    confidence            decimal
    evidence_path         text (path to the snapshot or clip, NOT the file itself)

INDEXES on: timestamp, camera_id, infraction_type
    // makes filtering and sorting fast when you have thousands of alerts

OPTIONAL TABLE video_jobs:
    id, video_path, camera_id, status, progress, error_message,
    created_at, finished_at

OPTIONAL TABLE cameras:
    id, name, location, lane_config
```

```
// session.py
FUNCTION create_connection():
    read database URL from config
    create a reusable pool of connections

FUNCTION get_session():
    open a session
    GIVE it to whoever asked
    WHEN they are finished:
        commit if everything worked, or roll back if there was an error
        close the session
```

**Concept to learn:** always store the **path** to the evidence file, not the video itself. Databases are poor places for large binary files.

---

### 3.11 `pipeline.py`: the conductor (most important pseudocode)

This is the heart of Netra. If you understand this block, you understand the project.

```
FUNCTION process_video(video_path, camera_id):

    // ---------- SETUP ----------
    open the video
    read fps, width, height, total frame count
    prepare an output video writer in processed_videos/

    lanes, counting_line = load_lane_config(camera_id)
    speed_transform = load calibration for camera_id (if available)

    alerted = empty set of (track_id, infraction_type)
    last_alert_time = empty map
    frame_number = 0

    // ---------- MAIN LOOP ----------
    WHILE the video has another frame:
        frame = read next frame
        frame_number = frame_number + 1
        current_time = frame_number / fps

        // optional speed-up: process only every Nth frame
        IF frame_number is not a multiple of FRAME_SKIP:
            write frame to output unchanged
            CONTINUE

        // STEP 1: detect and track
        vehicles = detect_and_track(frame)

        // STEP 2: update memory
        update_history(vehicles, frame_number)

        // STEP 3: understand speeds (if calibrated)
        speeds = empty map
        FOR EACH vehicle:
            speeds[vehicle.track_id] = estimate_speed(vehicle.track_id, fps)

        // STEP 4: apply rules
        events = run_all_rules(vehicles, lanes, counting_line)
        add accident events   from check_accident(vehicles, speeds, current_time)
        add gridlock events   from check_gridlock(...) for each lane

        // STEP 5: turn events into alerts (avoid spam)
        FOR EACH event in events:
            key = (event.track_id, event.type)
            IF key is in alerted:
                CONTINUE     // already reported this one
            add key to alerted

            snapshot_path = save current annotated frame as an image
            alert = build alert (camera, vehicle type, time, type,
                                 severity, track id, confidence, snapshot_path)
            save alert to database
            broadcast_alert(alert)       // live push to dashboard

        // STEP 6: draw on the frame
        draw_lanes(frame, lanes)
        FOR EACH vehicle:
            draw box, track id, class, speed (if known)
            colour red if the vehicle has an active violation
        draw total count on the frame
        write frame to output video

        // STEP 7: report progress
        update job progress = frame_number / total_frames

    // ---------- FINISH ----------
    close the video and the output writer
    RETURN summary: total vehicles counted, alerts by type
```

**Reading tip:** each STEP matches one file in `detection/`. Pipeline only coordinates and never contains rules itself.

---

### 3.12 Frontend pseudocode

#### `services/apiClient`

```
FUNCTION upload_video(file, camera_id):
    send file to the upload endpoint
    RETURN job id

FUNCTION get_job_status(job_id):
    ask the status endpoint
    RETURN status and progress

FUNCTION fetch_alerts(filters, page):
    ask the alerts endpoint with the filters
    RETURN list and total
```

#### `services/alertSocket`

```
FUNCTION connect_alert_socket(on_new_alert):
    open a WebSocket to the live alerts route

    WHEN a message arrives:
        alert = read the message
        call on_new_alert(alert)

    WHEN the connection drops:
        wait a few seconds
        try to reconnect       // dashboards run for hours, so this matters
```

#### `pages/Dashboard`

```
STATE alerts          = empty list
STATE vehicle_count   = 0
STATE connection_ok   = false

WHEN the page opens:
    alerts = fetch the most recent alerts from the API
    connect_alert_socket(handler)

    handler(new_alert):
        put new_alert at the TOP of alerts
        keep only the newest ~50
        IF new_alert is Critical: show a visible highlight or sound

WHEN the page closes:
    close the socket

SHOW:
    VideoPlayer     (processed video)
    VehicleCounter  (vehicle_count)
    AlertTable      (alerts, with SeverityBadge in each row)
    TrafficChart    (counts per minute, violations by type)
```

#### `pages/UploadPage`

```
STATE selected_file, job_id, progress, status

WHEN user picks a file and clicks upload:
    job_id = upload_video(selected_file, camera_id)
    START polling every few seconds:
        status, progress = get_job_status(job_id)
        update the progress bar
        IF status is "done":  stop polling, show "view results"
        IF status is "failed": stop polling, show error
```

---

## 4. Key Logic Concepts (Cheat Sheet)

| Concept | One-line explanation | Where it is used |
| --- | --- | --- |
| **Ground point** | Use the bottom-center of a box because that is where the vehicle touches the road. | Lane checks, speed |
| **Track ID** | A number that follows one vehicle across frames. | Everything that needs history |
| **Movement vector** | Newest position minus oldest position. Gives direction and distance. | Wrong-way, stopped detection |
| **Dot product** | Tells you if two directions agree or oppose. | Wrong-way |
| **Point in polygon** | Is this point inside this shape? | Finding which lane a vehicle is in |
| **Line intersection / side test** | Did the path of a vehicle cross a line? | Counting, lane crossing |
| **Confirmation counter** | Require a condition to be true N times in a row before acting. | Reducing false alarms |
| **Deduplication set** | Remember what you already reported. | Alert spam prevention |
| **Cooldown timer** | Do not repeat the same type of alert for a while. | Alert spam prevention |
| **Homography / calibration** | A mapping from image pixels to real-world meters. | Speed estimation |
| **IoU (overlap)** | How much two boxes overlap, from 0 to 1. | Accident signals |
| **Multi-signal scoring** | Combine several weak clues into one stronger decision. | Accident detection |
| **Background task** | Run slow work outside the web request. | Video processing |

---

## 5. Recommended Build Order

Build and test each milestone before starting the next. Each has a clear "done when" check.

| # | Milestone | Files involved | Done when |
| --- | --- | --- | --- |
| 1 | Detect vehicles in a video and draw boxes | `vehicle_detector.py`, a tiny test script | You can watch a video with boxes on every car |
| 2 | Add tracking and IDs | `vehicle_tracker.py` | The same car keeps the same ID for most of its journey |
| 3 | Count vehicles | `violation_detector.py` (counting only), `lane_detector.py` (counting line) | The count roughly matches what you count by eye |
| 4 | Define lanes | `lane_detector.py` | Lane polygons are drawn correctly over the video |
| 5 | Wrong-way and lane crossing | `violation_detector.py` | A test video triggers the right alerts at the right times |
| 6 | Save alerts | `models.py`, `session.py`, `pipeline.py` | Alerts appear in PostgreSQL with evidence snapshots |
| 7 | Wrap it in an API | `main.py`, `videos.py`, `alerts.py`, `schemas.py` | You can upload a video and read alerts from the API docs page |
| 8 | Build the dashboard | `frontend/` | Alerts show up live without refreshing |
| 9 | Speed and gridlock | `speed_estimator.py` | Measured speed on a known test video is believable |
| 10 | Accident candidate detection | `accident_detector.py` | Stopped-car scenarios are flagged, and normal red-light stops are not |

Do not start milestone 9 or 10 until 1 to 8 work. The advanced features depend on solid detection and tracking.

---

## 6. Common Pitfalls

1. **Loading the model per frame or per request.** Load once at startup.
2. **Using the box center instead of the bottom-center** for lane checks. Vehicles appear to be in the wrong lane.
3. **Trusting direction from too few frames.** Tracking jitter looks like movement. Use a minimum distance and a confirmation counter.
4. **No alert deduplication.** One violation can create hundreds of identical rows.
5. **Treating a stopped car as an accident.** Always combine signals and add a time requirement.
6. **Skipping calibration for speed.** Pixel speed is not real speed.
7. **Relying on automatic lane detection alone.** Shadows, curves, and worn paint will fool Canny + Hough. Use it to suggest, and configure the final lanes.
8. **Processing video inside the API request.** The request will time out. Use a background task.
9. **Storing video files in the database.** Store file paths instead.
10. **Never testing on different footage.** Day, night, rain, and different camera angles all behave differently.

---

## 7. Practice Exercises (to Build Your Logical Thinking)

Try these on paper before looking at the pseudocode above.

1. **Counting line.** A car is at position (100, 200) in one frame and (100, 220) in the next. A horizontal counting line sits at y = 210. Was the car counted? What if it appears again at y = 205 later?
2. **Wrong-way.** Lane direction is "up" (toward smaller y). A car moved from y = 400 to y = 450 over 10 frames. Is it wrong-way? What if it only moved 3 pixels?
3. **Dedup.** The same wrong-way car stays detected for 200 frames. How many alerts should exist, and what data structure guarantees that?
4. **Accident vs red light.** Five cars are stopped at a red light. One car stopped suddenly in the middle of a moving lane with another car's box overlapping it. Which signals fire for each case, and what score does each get?
5. **Gridlock timer.** Average speed is low for 20 seconds, then rises for 2 seconds, then drops again. Does gridlock fire at 30 seconds? Should it? How would you change the logic to handle brief gaps?
6. **Design question.** Where would you add a new rule, such as "no stopping in the bus lane"? Which existing files change, and which stay untouched?

If you can answer all six, you understand the logic of Netra, and writing the code will mostly be translation.

---

## 8. Licensing Reminder

Ultralytics YOLO is offered under AGPL-3.0 and an Enterprise license. Review the terms before any commercial deployment.
