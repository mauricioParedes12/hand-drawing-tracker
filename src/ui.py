import cv2
from config import *

def draw_palette(img, highlight_idx=None):
    overlay = img.copy()
    alpha = 0.65
    bar_h = 120
    y1 = hCam - bar_h

    cv2.rectangle(overlay, (0, y1), (wCam, hCam), (30, 30, 30), -1)

    x = 600
    for i, col in enumerate(colors):
        x1, x2 = x, x + 120
        y2 = hCam - 20

        if highlight_idx == i:
            cv2.rectangle(overlay, (x1 - 5, y1 + 5), (x2 + 5, y2 + 5), (255,255,255), -1)

        cv2.rectangle(overlay, (x1, y1 + 10), (x2, y2), col, -1)
        cv2.putText(overlay, color_names[i], (x1 + 10, y2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255,255,255), 2)

        x += 150

    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)


def draw_status_bar(img, text):
    overlay = img.copy()
    alpha = 0.55
    cv2.rectangle(overlay, (0, hCam - 60), (520, hCam), (20, 20, 20), -1)
    cv2.putText(overlay, text, (20, hCam - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
