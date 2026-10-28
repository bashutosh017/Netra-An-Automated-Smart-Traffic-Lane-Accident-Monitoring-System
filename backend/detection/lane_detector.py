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
    
