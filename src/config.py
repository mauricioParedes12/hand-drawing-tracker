import numpy as np # Librería para manejar matrices
import cv2 # Librería para capturar video y dibujar
import os # Para manejar carpetas y archivos
import mediapipe as mp # Librería que usa IA para detectar las manos

# Tamaño de la cámara
wCam, hCam = 1280, 720
proc_scale = 0.5 # Reducción de escala

# Grosor inicial del pincel y borrador
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
mp_hands = mp.solutions.hands # Módulo principal de manos
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) # Config para detectar una mano

# Canvas
canvas = np.zeros((hCam, wCam, 3), dtype=np.uint8)

# Directorio de guardado
SAVE_FOLDER = "saved_drawings"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Estabilización para evitar trazo que tiembla
smooth_factor = 0.40

# Valores del pinch (grosor)
pinch_thresh_small = 30
min_brush, max_brush = 1, 50

