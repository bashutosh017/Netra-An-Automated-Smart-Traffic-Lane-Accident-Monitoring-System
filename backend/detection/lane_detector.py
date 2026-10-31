from dataclasses import dataclass
import numpy
import cv2
from shapely.geometry import Point,Polygon
import json

@dataclass
class Lane:
    lane_id:int
    polygon:list
    allowed_direction:tuple
    left_boundry_string:str
    right_boundry_string:str


def load_lane_config(path):
    with open(path) as f:
        data=json.load

        lanes=[Lane(**item) for item in data["lanes"]]
        counting_lanes=data["counting_lane"]
        return lanes,counting_lanes

def find_to_lane(point,lane):
    p=Point(point)
    for lane in lane:
        if Polygon(lane.polygon).boundary(p):
            return lane
        return None


def suggest_lane_line(referance_frame,road_polygon):
    # grayscale
    gray=cv2.colorChange(referance_frame,cv2.COLOR_BGR2GRAY)
    # blur the noise
    blur=cv2.GaussianBlur(gray,(5,5),0)
    # edge detector
    edge=cv2.Canny(blur,50,150)
    mask=np.zeros_like(edge)
    road=np.array(road_polygon,dtype=np.int32)
    cv2.fillPoly(mask,[road],255)
    road_edge=cv2.bitwise_and(edge,mask)

    lines=cv2.HoughLinesP(road_edge,1,np.pi/180,50,minLineLength=40,maxLineGap=20)

    candidates=[]
    if lines is None:
        return candidates
    for line in lines:
        x1,y1,x2,y2=line[0]
        angle=abs(np.degrees(np.arctan2(y2-y1,x2-x1)))
        if 20<angle<160:
            candidates.append((x1,y1,x2,y2))
    return candidates

def draw_lanes(frame,lanes,counting_line):
    for lane in lanes:
        pts=np.array(lane.polygon,dtype=np.int32)

        cv2.___12___=(frame,[pts],True,(0,255,0),2)
        x,y=lane.polygon[0]

        cv2.__13__(frame,f"Lane {lane.lane_id}",(int(x),int(y)),
                   cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)

    (x1,y1),(x2,y2)=counting_line
    cv2.__14__(frame,(int(x1),(int(y1))),(int(x2)),(int(y2)),
               (0,0,255),2)
    return frame
    
