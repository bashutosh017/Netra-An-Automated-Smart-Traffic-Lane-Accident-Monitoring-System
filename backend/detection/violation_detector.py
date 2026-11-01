import numpy as np
from collections import defaultdict
from shapely.geometry import LineString

MIN_MOVEMENT = 15
FRAMES = 5

counted_ids = set()
wrong_count = defaultdict(int)


def side_of_line(point, line):
    """Return 1, -1, or 0 depending on which side of the line the point is on."""
    (ax, ay), (bx, by) = line
    px, py = point
    cross = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
    if cross > 0:
        return 1
    if cross < 0:
        return -1
    return 0


def check_counting_line(track_id, previous_point, current_point, line):
    """Return a 'counted' event the first time a vehicle crosses the counting line."""
    if track_id in counted_ids:
        return None

    before = side_of_line(previous_point, line)
    now = side_of_line(current_point, line)

    if before != now:
        counted_ids.add(track_id)
        return {"type": "counted", "track_id": track_id}
    return None


def get_total_count():
    """Return how many different vehicles have been counted."""
    return len(counted_ids)


def check_wrong_way(track_id, movement, lane):
    """Return a 'wrong-way' event after several readings against the lane direction."""
    if movement is None:
        return None

    length = np.linalg.norm(movement)
    if length < MIN_MOVEMENT:
        return None

    alignment = np.dot(movement, lane.allowed_direction)

    if alignment < 0:
        wrong_count[track_id] += 1
    else:
        wrong_count[track_id] = 0

    if wrong_count[track_id] >= FRAMES:
        return {
            "type": "wrong-way",
            "severity": "Critical",
            "track_id": track_id,
        }
    return None


def check_lane_crossing(track_id, previous_point, current_point, boundaries):
    """Return a 'lane violation' event if the vehicle's path crossed a solid boundary."""
    path = LineString([previous_point, current_point])

    for boundary in boundaries:
        if boundary["type"] == "solid":
            line = LineString(boundary["points"])
            if path.intersects(line):
                return {
                    "type": "lane violation",
                    "severity": "Warning",
                    "track_id": track_id,
                }
    return None


def run_all_rules(vehicles, counting_line, boundaries):
    """Run every rule on every vehicle and return the list of events."""
    events = []

    for v in vehicles:
        if v["previous_point"] is None:
            continue

        results = [
            check_counting_line(v["track_id"], v["previous_point"], v["current_point"], counting_line),
            check_lane_crossing(v["track_id"], v["previous_point"], v["current_point"], boundaries),
        ]

        if v["lane"] is not None:
            results.append(check_wrong_way(v["track_id"], v["movement"], v["lane"]))

        for event in results:
            if event is not None:
                events.append(event)

    return events
