import cv2
from config import *

def merge_canvas(frame, canvas):
    # Pasamos el canvas a gris para detectar dónde hay trazos de dibujo
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)

    # Creamos una máscara
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    
    inv = cv2.bitwise_not(mask) # Invertimos máscara para performar video original en la zona de dibujo

    bg = cv2.bitwise_and(frame, frame, mask=inv) # Recortamos espacio de dibujo
    
    fg = cv2.bitwise_and(canvas, canvas, mask=mask) # Se extrae solo trazos de colores del canvas

    return cv2.add(bg, fg) 
