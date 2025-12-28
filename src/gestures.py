import math
from config import *
from utils import fingers_up

# Umbral de distancia entre pulgar e índice para detectar un pellizco
PINCH_THRESHOLD_NORM = 0.055
# Cuántos frames debe mantenerse el pellizco para considerarse válido 
PINCH_STABLE_FRAMES = 2

def process_gestures(lm, canvas, state):
    # Convertimos las coordenadas de MediaPipe (0 a 1) a píxeles de nuestra pantalla
    raw_ix_px = int(lm[8].x * wCam)
    raw_iy_px = int(lm[8].y * hCam)

    # Filtro de suavizado: para que el punto no salte mucho por el ruido de la cámara
    if state.get("stabilized_ix") is None:
        state["stabilized_ix"] = raw_ix_px
        state["stabilized_iy"] = raw_iy_px
    else:
        sf = smooth_factor
        state["stabilized_ix"] = int(state["stabilized_ix"] * (1 - sf) + raw_ix_px * sf)
        state["stabilized_iy"] = int(state["stabilized_iy"] * (1 - sf) + raw_iy_px * sf)

    ix, iy = state["stabilized_ix"], state["stabilized_iy"]

    # Chequeamos qué dedos están arriba [pulgar, índice, medio, anular, meñique]
    up = fingers_up(lm) 
    total_up = sum(up) 
    index_up = up[1]   
    middle_up = up[2]  

    # Detectamos el pellizco (distancia entre el pulgar e índice) para el grosor
    thumb = (lm[4].x, lm[4].y)
    index = (lm[8].x, lm[8].y)
    pinch_dist_norm = math.dist(thumb, index) # Distancia euclidiana
    
    # Verificamos si la distancia es menor al umbral definido
    is_pinch_raw = pinch_dist_norm < PINCH_THRESHOLD_NORM

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
