import cv2
from config import *

def draw_palette(img, highlight_idx=None):
    # Dibuja la barra inferior con los colores disponibles para elegir
    overlay = img.copy() # copia para transparencia
    alpha = 0.65 
    bar_h = 120
    y1 = hCam - bar_h # posición vertical de barra

    cv2.rectangle(overlay, (0, y1), (wCam, hCam), (30, 30, 30), -1)

    x = 600
    for i, col in enumerate(colors):
        x1, x2 = x, x + 120
        y2 = hCam - 20

        # Si color seleccionado, dibujamos borde blanco
        if highlight_idx == i:
            cv2.rectangle(overlay, (x1 - 5, y1 + 5), (x2 + 5, y2 + 5), (255,255,255), -1)

        cv2.rectangle(overlay, (x1, y1 + 10), (x2, y2), col, -1)
        cv2.putText(overlay, color_names[i], (x1 + 10, y2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255,255,255), 2)

        x += 150

    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

def draw_thickness_bar(img, thickness):
    # Dibuja una barra vertical a la izquierda que indica el grosor del pincel
    overlay = img.copy()
    alpha = 0.55

    bar_x1 = 50
    bar_y1 = 100
    bar_x2 = 80
    bar_y2 = hCam - 100

    # Fondo de la barra
    cv2.rectangle(overlay, (bar_x1, bar_y1), (bar_x2, bar_y2), (40, 40, 40), -1)

    # Rango total de la barra
    total_height = bar_y2 - bar_y1

    # Convertir grosor a porcentaje
    pct = (thickness - min_brush) / float(max_brush - min_brush)
    pct = max(0, min(1, pct))  # clamp

    bar_fill_top = int(bar_y2 - pct * total_height)

    # Relleno dinámico (grosor)
    cv2.rectangle(overlay, (bar_x1, bar_fill_top), (bar_x2, bar_y2), (0, 255, 255), -1)

    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

def draw_status_bar(img, text):
    # Dibuja un cuadro de texto en la esquina inferior izquierda con el estado actual
    overlay = img.copy()
    alpha = 0.55
    cv2.rectangle(overlay, (0, hCam - 60), (520, hCam), (20, 20, 20), -1)
    cv2.putText(overlay, text, (20, hCam - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

def draw_save_progress(img, progress):
    # Dibuja una barra central que se llena mientras se mantiene el gesto de guardar
    overlay = img.copy()
    alpha = 0.60

    # Tamaño de la barra
    bar_width = 400
    bar_height = 45

    h, w, _ = img.shape

    # Centro de la pantalla
    x1 = (w - bar_width) // 2
    y1 = (h - bar_height) // 2
    x2 = x1 + bar_width
    y2 = y1 + bar_height

    # Barra de fondo (gris)
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (50, 50, 50), -1)

    # Barra verde de avance
    bar_fill = int(progress * bar_width)
    cv2.rectangle(overlay, (x1, y1), (x1 + bar_fill, y2), (0, 200, 0), -1)

    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

