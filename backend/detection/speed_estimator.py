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

    x1,y1,frame1=points[0]
    x2,y2,frame2=points[-1]

    start=to_Road_meters((x1,y1),transform)
    end=to_Road_meters((x2,y2),transform)

    dist_m=np.linalg.norm(end-start)

    seconds=(frame2-frame2)/fps

    if seconds<=0:
        return None

    speed_mps=dist_m/seconds
    return speed_mps*1000

def SmoothSpeed(track_id,speed):
    if speed is None:
        return None
    recent_speed[track_id].append(speed)
    return np.median(recent_speed[track_id])

def CheckGridlock(lane_id,speeds,now_time):
    known=[s for s in speeds if s is not None]

    if len(known)>=MIN_VEHICLES and np.mean(known):
        if lane_id not in gridlock_since:
            gridlock_since[lane_id]=now_time
        elif now_time-gridlock_since[lane_id]>=MIN_DURATION:
            return{
                "type":"gridlock",
                "serverity":"Warning!",
                "lane_id":lane_id,
            }
        else:
            gridlock_since.pop(lane_id,None)


