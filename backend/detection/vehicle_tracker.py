from collections import deque,defaultdict
# from ultralytics import YOLO
import math

# model=YOLO("yolov8n.pt")

MAX_HISTORY=30
MAX_MISSING_FRAMES=60

history=defaultdict(lambda:deque(maxlen=MAX_HISTORY))
last_seen={}

def ground_point(box):
    left,top,right,bottom=box
    x=(left+right)/2
    y=bottom
    return (x,y)

def update_history(vehicles,frame_number):
    for vehicle in vehicles:
        track_id=vehicle["tracking_id"]
        x,y=ground_point(vehicle["box"])
        history[track_id].append(x,y,frame_number)
        last_seen[track_id]=frame_number

        stale_ids = [
        tid for tid, seen in last_seen.items()
        if frame_number - seen > MAX_MISSING_FRAMES
    ]
    for tid in stale_ids:
        del history[tid]
        del last_seen[tid]


def get_movement_vector(track_id):
    if track_id not in history or len(history[track_id]) < 2:
        return None
    oldest = history[track_id][0]
    newest = history[track_id][-1]
    return (newest[0] - oldest[0], newest[1] - oldest[1])


def get_displacement(track_id):
    vector = get_movement_vector(track_id)
    if vector is None:
        return None
    return math.hypot(vector[0], vector[1])