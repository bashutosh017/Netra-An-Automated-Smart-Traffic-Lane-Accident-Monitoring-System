from collections import defaultdict,deque

STOP_DISP=5
STOP_DUR=10
FAST_SPEED=3
SPEED_WINDOW=30
OVERLAP_LMT=0.3
STOP_SPEED=3
OVERLAP_SPEED=0.3
MOVING_DISP=15
SCORE_THERSHOLD=2
MAX_SCORE=4


stopped_since={}

speed_history=defaultdict(lambda:deque(maxlen=SPEED_WINDOW))

def iou(a,b):
    left=max(a[0],b[0])
    top=max(a[1],b[1])
    right=min(a[2],b[2])
    bottom=min(a[3],b[3])


    inter_w=max(0,right-left)
    inter
