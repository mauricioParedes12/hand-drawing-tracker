import cv2
from config import *

def fingers_up(lm):
    tips = [4, 8, 12, 16, 20]
    fingers = []
    fingers.append(lm[tips[0]].x < lm[3].x)
    for i in range(1, 5):
        fingers.append(lm[tips[i]].y < lm[tips[i] - 2].y)
    return fingers


def push_snapshot(canvas_img, snapshots, MAX_SNAPSHOTS=25):
    if len(snapshots) >= MAX_SNAPSHOTS:
        snapshots.pop(0)
    snapshots.append(canvas_img.copy())
