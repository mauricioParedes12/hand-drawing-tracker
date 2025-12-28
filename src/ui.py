import cv2
import math
from config import *

def draw_spatial_menu(img, current_ix, current_iy):
    # Creamos un menú en el centro tipo "cruz" para elegir color rápido
    overlay = img.copy()
    h, w, _ = img.shape
    center_x, center_y = w // 2, h // 2
    
    positions = [
        (center_x, center_y - 120),
        (center_x, center_y + 120),
        (center_x - 120, center_y),
        (center_x + 120, center_y)
    ]
    
    selected_idx = None
    base_radius = 45  # Radio normal
    expanded_radius = 60 # Radio cuando el dedo está encima

    for i, pos in enumerate(positions):
        col = colors[i]
        # Calculamos la distancia entre el dedo índice y el centro de cada círculo
        distance = math.hypot(current_ix - pos[0], current_iy - pos[1])
        
        # Efecto de agrandamiento del círculo
        if distance < expanded_radius:
            current_radius = expanded_radius
            selected_idx = i
            # Dibujamos un resplandor o borde blanco grueso
            cv2.circle(overlay, pos, current_radius + 5, (255, 255, 255), -1)
        else:
            current_radius = base_radius

        # Dibujamos el círculo del color correspondiente
        cv2.circle(overlay, pos, current_radius, col, -1)
        # Borde negro fino para que el color resalte más
        cv2.circle(overlay, pos, current_radius, (0, 0, 0), 2)

    return cv2.addWeighted(overlay, 0.7, img, 0.3, 0), selected_idx

def draw_thickness_bar(img, thickness):
    overlay = img.copy()
    alpha = 0.55 # Transparencia de la barra de grososr
    bar_x, bar_y, bar_w, bar_h = 50, 150, 25, 400 # Posición y dimensión fija de la barra

    # Dibujamos fondo gris de la barra
    cv2.rectangle(overlay, (bar_x-2, bar_y-2), (bar_x+bar_w+2, bar_y+bar_h+2), (200, 200, 200), 1)
    cv2.rectangle(overlay, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (30, 30, 30), -1)

    # Llenado de la barra dinámico
    pct = (thickness - min_brush) / float(max_brush - min_brush)
    fill_h = int(pct * bar_h)
    
    # Color cian para el progreso
    cv2.rectangle(overlay, (bar_x, bar_y + bar_h - fill_h), (bar_x + bar_w, bar_y + bar_h), (255, 255, 0), -1)

    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

def draw_status_bar(img, text, current_color=(255, 255, 255)):
    h, w, _ = img.shape
    overlay = img.copy()
    
    # Definimos el tamaño de la barra de estado
    bar_w, bar_h = 420, 50 
    x1, y1 = 15, h - bar_h - 15
    x2, y2 = x1 + bar_w, h - 15
    
    # Aplicamos desenfoque a la barra
    sub_img = img[y1:y2, x1:x2]
    blur_zone = cv2.GaussianBlur(sub_img, (15, 15), 0)
    overlay[y1:y2, x1:x2] = blur_zone

    # Se agrega fondo oscuro con transparencia y borde blanco fino
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (20, 20, 20), -1)
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255), 1, cv2.LINE_AA)

    # Dibujamos un círculo pequeño que indica el color actual
    cv2.circle(overlay, (x1 + 25, y1 + bar_h // 2), 10, current_color, -1)
    cv2.circle(overlay, (x1 + 25, y1 + bar_h // 2), 11, (255, 255, 255), 1, cv2.LINE_AA)

    # Se agrega texto que indica estados en mayúscula
    font = cv2.FONT_HERSHEY_DUPLEX
    text_pos = (x1 + 50, y1 + 33) 
    cv2.putText(overlay, text.upper(), text_pos, font, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(overlay, text.upper(), text_pos, font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    # Mezcla final
    return cv2.addWeighted(overlay, 0.8, img, 0.2, 0) 

def draw_save_progress(img, progress):
    overlay = img.copy()
    h, w, _ = img.shape

    # Definimos posición y dimensiones de la barra de guardado
    bar_w, bar_h = 450, 40
    x1 = (w - bar_w) // 2
    y1 = (h - bar_h) // 2
    x2, y2 = x1 + bar_w, y1 + bar_h

    # Sombra exterior de la barra
    cv2.rectangle(overlay, (x1 - 5, y1 - 5), (x2 + 5, y2 + 5), (20, 20, 20), -1)
    
    # Fondo gris oscuro de la barra
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (40, 40, 40), -1)

    # Cálculo del progreso
    bar_fill = int(progress * bar_w)

    if bar_fill > 0:
        # Carga de color verde de la barra
        cv2.rectangle(overlay, (x1, y1), (x1 + bar_fill, y2), (0, 255, 0), -1)
        
        # Detalle de brillo superior blanco
        cv2.line(overlay, (x1, y1 + 5), (x1 + bar_fill, y1 + 5), (200, 255, 200), 2)

    # Aplicamos la transparencia
    return cv2.addWeighted(overlay, 0.8, img, 0.2, 0)
