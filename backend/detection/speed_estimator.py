IN_POINTS = 5        # history points needed before we trust a speed
SMOOTHING = 7         # how many recent speeds we take the middle value of
SLOW_SPEED = 5        # km/h: below this, traffic counts as "crawling"
MIN_VEHICLES = 8      # vehicles needed in a lane for gridlock
MIN_DURATION = 30     # seconds the lane must stay slow before gridlock is declared
 
# ---------------------------------------------------------------- MEMORY
recent_speeds = defaultdict(lambda: deque(___7___=SMOOTHING))   # HINT 7: the deque size-limit argument you learned in vehicle_tracker
gridlock_since = {}                                              # lane_id -> time the slow period started
 
 
