import math
from config import *
from utils import fingers_up

# Umbral de distancia entre pulgar e índice para detectar un pellizco (normalizado de 0 a 1)
PINCH_THRESHOLD_NORM = 0.055
# Cuántos frames debe mantenerse el pellizco para considerarse válido (evita falsos positivos)
PINCH_STABLE_FRAMES = 2

def process_gestures(lm, canvas, state):
    # Analiza posición de landmarks para determinar gesto
    
    # 1. Obtener coordenadas actuales de la punta del dedo índice (punto 8)
    raw_ix_px = int(lm[8].x * wCam)
    raw_iy_px = int(lm[8].y * hCam)

    # 2. Algoritmo de Suavizado (Filtro de media móvil simple)
    # Si es el primer frame, inicializamos la posición estabilizada
    if state.get("stabilized_ix") is None:
        state["stabilized_ix"] = raw_ix_px
        state["stabilized_iy"] = raw_iy_px
    else:
        # Mezclamos la posición anterior con la nueva usando el smooth_factor de config.py
        # Esto elimina el temblor natural de la mano
        sf = smooth_factor
        state["stabilized_ix"] = int(state["stabilized_ix"] * (1 - sf) + raw_ix_px * sf)
        state["stabilized_iy"] = int(state["stabilized_iy"] * (1 - sf) + raw_iy_px * sf)

    # Coordenadas finales que usaremos para dibujar
    ix, iy = state["stabilized_ix"], state["stabilized_iy"]

    # 3. Análisis de dedos levantados
    up = fingers_up(lm) # Lista de 5 valores [pulgar, índice, medio, anular, meñique] (1=arriba, 0=abajo)
    total_up = sum(up) # Cantidad total de dedos levantados
    index_up = up[1]   # Estado específico del índice
    middle_up = up[2]  # Estado específico del dedo medio

    # 4. Detección de Pellizco (Pinch) para el grosor
    # Comparamos la distancia entre la punta del pulgar (4) y la del índice (8)
    thumb = (lm[4].x, lm[4].y)
    index = (lm[8].x, lm[8].y)
    pinch_dist_norm = math.dist(thumb, index) # Distancia euclidiana
    
    # Verificamos si la distancia es menor al umbral definido
    is_pinch_raw = pinch_dist_norm < PINCH_THRESHOLD_NORM

    # 5. Estabilización del pellizco (debouncing)
    # Incrementamos el contador si hay pellizco, de lo contrario reseteamos a 0
    pinch_count = state.get("pinch_count", 0)
    pinch_count = pinch_count + 1 if is_pinch_raw else 0
    state["pinch_count"] = pinch_count

    # Solo activamos is_pinch si se mantiene por varios frames seguidos
    is_pinch = pinch_count >= PINCH_STABLE_FRAMES

    # Retornamos toda la información procesada en un paquete
    return {
        "ix": ix,
        "iy": iy,
        "up": up,
        "total_up": total_up,
        "index_up": index_up,
        "middle_up": middle_up,
        "is_pinch": is_pinch
    }
