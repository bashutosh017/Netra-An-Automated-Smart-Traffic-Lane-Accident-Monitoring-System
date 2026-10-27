# import cv2
from ultralytics import YOLO
# import numpy as np

model=YOLO("yolov8n.pt")
CLASS=[3,4,6,8]
MIN_CONFIDENSE=0.45

# cap=cv2.VideoCapture(0)
# while cap.isOpened():
#     frame,ret=cap.read()
#     if not ret:
#         break

def detect_and_track(frame):
    result=model.track(
        frame,
        persist=True,
        conf=MIN_CONFIDENSE,
        classes=CLASS,
        tracker="bytetrack.yaml",
        verbose=False,
    )

    vechicle=[]
    boxes=result[0].boxes

    if boxes.id is None:
        return vechicle

    for box, tracking_id,cls, conf in zip(boxes.xyxy,boxes.id,boxes.cls,boxes.conf):
        vechicle.append({
            "track_id":int(tracking_id),
            "class_name":model.names[int(cls)],
            "box":box.tolist(),
            "confidence":float(conf),
        })
    
    return vechicle