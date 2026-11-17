from collections import defaultdict, deque

STOP_DISPLACEMENT = 5
STOP_DURATION = 10
FAST_SPEED = 30
STOP_SPEED = 3
SPEED_WINDOW = 30
OVERLAP_LIMIT = 0.3
MOVING_DISPLACEMENT = 15
SCORE_THRESHOLD = 2
MAX_SCORE = 4

stopped_since = {}
speed_history = defaultdict(lambda: deque(maxlen=SPEED_WINDOW))


def iou(a, b):
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])

    inter_w = max(0, right - left)
    inter_h = max(0, bottom - top)
    intersection = inter_w * inter_h

    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - intersection

    if union == 0:
        return 0
    return intersection / union


def check_accidents(vehicles, current_time):
    events = []

    for v in vehicles:
        track_id = v["track_id"]
        score = 0

        is_stopped = v["displacement"] is not None and v["displacement"] < STOP_DISPLACEMENT
        if is_stopped:
            if track_id not in stopped_since:
                stopped_since[track_id] = current_time
            if current_time - stopped_since[track_id] >= STOP_DURATION:
                score += 1
        else:
            stopped_since.pop(track_id, None)

        speed = v["speed"]
        if speed is not None:
            speed_history[track_id].append(speed)
            if max(speed_history[track_id]) >= FAST_SPEED and speed <= STOP_SPEED:
                score += 1

        for other in vehicles:
            if other["track_id"] == track_id:
                continue
            if iou(v["box"], other["box"]) >= OVERLAP_LIMIT:
                score += 1
                break

        if is_stopped:
            neighbours_moving = any(
                o["displacement"] is not None and o["displacement"] > MOVING_DISPLACEMENT
                for o in vehicles
                if o["track_id"] != track_id and o["lane_id"] == v["lane_id"]
            )
            if neighbours_moving:
                score += 1

        if score >= SCORE_THRESHOLD:
            events.append({
                "type": "accident",
                "severity": "Critical",
                "track_id": track_id,
                "confidence": round(score / MAX_SCORE, 2),
            })

    return events


def forget_missing(active_ids):
    for store in (stopped_since, speed_history):
        for track_id in list(store):
            if track_id not in active_ids:
                del store[track_id]
