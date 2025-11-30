import cv2
from config import *
from utils import push_snapshot, fingers_up

def process_gestures(lm, canvas, state):
    hCam_local = hCam
    wCam_local = wCam

    raw_ix = int(lm[8].x * wCam_local)
    raw_iy = int(lm[8].y * hCam_local)

    # Estabilización
    if state["stabilized_ix"] is None:
        state["stabilized_ix"] = raw_ix
        state["stabilized_iy"] = raw_iy
    else:
        state["stabilized_ix"] = int(state["stabilized_ix"] * (1 - smooth_factor) + raw_ix * smooth_factor)
        state["stabilized_iy"] = int(state["stabilized_iy"] * (1 - smooth_factor) + raw_iy * smooth_factor)

    ix, iy = state["stabilized_ix"], state["stabilized_iy"]

    up = fingers_up(lm)
    total_up = sum(up)
    index_up = up[1]
    middle_up = up[2]

    # pinch detection
    dx = (lm[4].x - lm[8].x) * wCam_local
    dy = (lm[4].y - lm[8].y) * hCam_local
    pinch_dist = (dx*dx + dy*dy) ** 0.5
    is_pinch = pinch_dist < pinch_thresh_small and not middle_up and not up[3] and not up[4]

    return {
        "ix": ix,
        "iy": iy,
        "up": up,
        "total_up": total_up,
        "index_up": index_up,
        "middle_up": middle_up,
        "is_pinch": is_pinch
    }
