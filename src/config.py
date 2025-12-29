import numpy as np 
import os 
import mediapipe as mp 

# Seteamos la resolución de la cámara (HD)
wCam, hCam = 1280, 720
proc_scale = 0.2 # Bajamos la escala a 0.3 para que la IA procese menos píxeles y no se laguee

# Configuramos grosores iniciales
brushThickness = 8
eraserThickness = 50

# Colores disponibles
colors = [
    (0, 0, 255),  # Rojo
    (0, 255, 0),  # Verde
    (255, 0, 0),  # Azul
    (0, 255, 255) # Amarillo
]
color_names = ["Rojo", "Verde", "Azul", "Amarillo"]

# Configuramos MediaPipe para que detecte solo 1 mano con un 70% de confianza
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) 

# Creamos el 'lienzo' negro donde se guardará nuestro dibujo
canvas = np.zeros((hCam, wCam, 3), dtype=np.uint8)

# Creamos la carpeta de fotos si no existe
SAVE_FOLDER = "saved_drawings"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Estabilización para evitar trazo que tiembla
smooth_factor = 0.40

# Valores del pinch (grosor)
pinch_thresh_small = 30
min_brush, max_brush = 1, 50

