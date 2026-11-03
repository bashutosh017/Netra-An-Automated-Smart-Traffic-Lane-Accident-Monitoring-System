import cv2
from collections import deque,defaultdict
import numpy as np

MIN_POINTS=5
SMOOTHING=7
SLOW_SPEED=5
MIN_VEHICLES=8
MIN_DURATION=30


recent_speed=defaultdict(lambda:deque(maxlen=SMOOTHING))
gridlock_since={}

def build_transform(image_points,real_points):
    src=np.array(image_points,dtype=np.float32)
    dst=np.array(real_points,dtype=np.float32)
    return cv2.getPerspectiveTransform(src,dst)

def to_Road_meters(point,transform):
    p=np.array([[point]],dtype=np.float32)
    result=cv2.perspectiveTransform(p,transform)
    return result[0][0]

def estimate_Speed(points,fps,transform):
    if len(points)<MIN_POINTS:
        return None

    
