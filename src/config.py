import numpy as np
import cv2
import os
import mediapipe as mp

# Tamaño de la cámara
wCam, hCam = 1280, 720
proc_scale = 0.5

# Pincel y borrador
brushThickness = 8
eraserThickness = 50

# Colores disponibles
colors = [
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (0, 255, 255)
]
color_names = ["Rojo", "Verde", "Azul", "Amarillo"]

# Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Canvas
canvas = np.zeros((hCam, wCam, 3), dtype=np.uint8)

# Directorio de guardado
SAVE_FOLDER = "saved_drawings"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Estabilización
smooth_factor = 0.40

# Valores del pinch (grosor)
pinch_thresh_small = 30
min_brush, max_brush = 1, 50

