import math
from config import *
from utils import push_snapshot, fingers_up

PINCH_THRESHOLD_NORM = 0.055
PINCH_STABLE_FRAMES = 2

def process_gestures(lm, canvas, state):

    raw_ix_px = int(lm[8].x * wCam)
    raw_iy_px = int(lm[8].y * hCam)

    if state.get("stabilized_ix") is None:
        state["stabilized_ix"] = raw_ix_px
        state["stabilized_iy"] = raw_iy_px
    else:
        sf = smooth_factor
        state["stabilized_ix"] = int(state["stabilized_ix"] * (1 - sf) + raw_ix_px * sf)
        state["stabilized_iy"] = int(state["stabilized_iy"] * (1 - sf) + raw_iy_px * sf)

    ix, iy = state["stabilized_ix"], state["stabilized_iy"]

    up = fingers_up(lm)
    total_up = sum(up)
    index_up = up[1]
    middle_up = up[2]

    thumb = (lm[4].x, lm[4].y)
    index = (lm[8].x, lm[8].y)
    pinch_dist_norm = math.dist(thumb, index)
    is_pinch_raw = pinch_dist_norm < PINCH_THRESHOLD_NORM

    pinch_count = state.get("pinch_count", 0)
    pinch_count = pinch_count + 1 if is_pinch_raw else 0
    state["pinch_count"] = pinch_count

    is_pinch = pinch_count >= PINCH_STABLE_FRAMES

    return {
        "ix": ix,
        "iy": iy,
        "up": up,
        "total_up": total_up,
        "index_up": index_up,
        "middle_up": middle_up,
        "is_pinch": is_pinch
    }
