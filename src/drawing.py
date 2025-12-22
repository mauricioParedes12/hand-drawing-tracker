import cv2
from config import *

def merge_canvas(frame, canvas):
    # Mezcla frame de cámara con dibujo de canvas usando máscaras de bits
    
    # 1. Convertimos el canvas a escala de grises para identificar dónde hay dibujo
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    
    # 2. Creamos una máscara: lo que NO es negro (dibujo) será blanco (255)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    
    # 3. Invertimos la máscara: lo que es dibujo será negro y el fondo será blanco
    # Esto nos servirá para "recortar" el hueco del dibujo en el video
    inv = cv2.bitwise_not(mask)

    # 4. Usamos la máscara invertida para limpiar el área del dibujo en el video original
    # Es como recortar un espacio en el video donde luego pegaremos el color
    bg = cv2.bitwise_and(frame, frame, mask=inv)
    
    # 5. Usamos la máscara original para extraer solo los trazos de colores del canvas
    # Quitamos todo el fondo negro y nos quedamos solo con la tinta del dibujo
    fg = cv2.bitwise_and(canvas, canvas, mask=mask)

    # 6. Sumamos ambas imágenes: el video con "huecos" + solo los colores del dibujo
    # El resultado es una fusión perfecta sin el fondo negro del canvas
    return cv2.add(bg, fg)
