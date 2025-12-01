import cv2
from config import *

def merge_canvas(frame, canvas):
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    inv = cv2.bitwise_not(mask)

    bg = cv2.bitwise_and(frame, frame, mask=inv)
    fg = cv2.bitwise_and(canvas, canvas, mask=mask)

    return cv2.add(bg, fg)
