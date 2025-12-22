import cv2
import numpy as np
import os

from config import *
from ui import draw_palette, draw_status_bar, draw_thickness_bar, draw_save_progress
from gestures import process_gestures
from drawing import merge_canvas

# -------------------------------------------------------------
# FUNCIÓN PARA GUARDAR EL DIBUJO CON FONDO BLANCO
# -------------------------------------------------------------
def save_canvas(canvas, counter):
    # Crear un fondo blanco del mismo tamaño que el dibujo
    white_bg = np.ones_like(canvas) * 255

    # Crear máscara para separar el dibujo del fondo negro original
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    # Combinar el dibujo con el fondo blanco
    bg = cv2.bitwise_and(white_bg, white_bg, mask=mask_inv)
    fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    final = cv2.add(bg, fg)

    # Guardar en la carpeta especificada
    filepath = os.path.join(SAVE_FOLDER, f"drawing_{counter}.png")
    cv2.imwrite(filepath, final)
    print(f"Imagen guardada en: {filepath}")

# -------------------------------------------------------------
# ESTADO INICIAL Y VARIABLES DE CONTROL
# -------------------------------------------------------------
state = {"stabilized_ix": None, "stabilized_iy": None}
palette_active = False
current_color = colors[0]
gesture_text = "Modo Normal"
xp, yp = 0, 0 # Coordenadas previas para dibujar líneas continuas

# Contadores de frames para validar gestos
required_frames = 4
erase_frames = select_frames = draw_frames = fist_frames = pinch_frames = 0
save_frames = 0
SAVE_REQUIRED_FRAMES = 40 # Tiempo que hay que mantener el gesto de guardado
save_counter = 1

# -------------------------------------------------------------
# CONFIGURACIÓN DE VIDEO
# -------------------------------------------------------------
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

WINDOW_NAME = "HandPicture"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

# -------------------------------------------------------------
# LOOP PRINCIPAL
# -------------------------------------------------------------
while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1) # Efecto espejo
    img = frame.copy()

    # Procesamiento con MediaPipe en imagen reducida para mayor fluidez
    small = cv2.resize(frame, (0, 0), fx=proc_scale, fy=proc_scale)
    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_small)

    highlight_idx = None
    is_pinch = False
    
    # Fusionar video y canvas al inicio para tener la base donde dibujar la UI
    combined = merge_canvas(img, canvas)  

    if result.multi_hand_landmarks:
        lm = result.multi_hand_landmarks[0].landmark

        # Extraer datos procesados de gestures.py
        G = process_gestures(lm, canvas, state)
        ix, iy, up, total_up = G["ix"], G["iy"], G["up"], G["total_up"]
        index_up, middle_up, is_pinch = G["index_up"], G["middle_up"], G["is_pinch"]

        # Reset de contadores si el gesto cambia
        if total_up != 5: erase_frames = 0
        if not (index_up and middle_up and total_up == 2): select_frames = 0
        if not (index_up and total_up == 1): draw_frames = 0
        if total_up != 0: fist_frames = 0
        if not is_pinch: pinch_frames = 0

        # LÓGICA DE GESTOS
        # 1. Gesto de Guardado (Spider-man / Cuernos)
        if up == [1, 0, 0, 0, 1]:
            save_frames += 1
            progress = min(save_frames / SAVE_REQUIRED_FRAMES, 1.0)
            gesture_text = "Guardando..."
            combined = draw_save_progress(combined, progress)

            if save_frames >= SAVE_REQUIRED_FRAMES:
                save_canvas(canvas, save_counter)
                save_counter += 1
                save_frames = 0
                gesture_text = "Imagen guardada"
        else:
            save_frames = 0

        # 2. Puño cerrado: Limpiar selección de colores
        if total_up == 0:
            fist_frames += 1
            if fist_frames >= required_frames:
                palette_active = False
                xp = yp = 0
                gesture_text = "Mano cerrada"

        # 3. Mano abierta: Borrador
        elif total_up == 5 and not palette_active:
            erase_frames += 1
            if erase_frames >= required_frames:
                if xp == 0 and yp == 0: xp, yp = ix, iy
                cv2.line(canvas, (xp, yp), (ix, iy), (0, 0, 0), eraserThickness)
                xp, yp = ix, iy
                gesture_text = "Borrando..."

        # 4. Dos dedos arriba: Abrir paleta y elegir color
        elif index_up and middle_up and total_up == 2:
            select_frames += 1
            if select_frames >= required_frames:
                palette_active = True
                xp = yp = 0
                gesture_text = "Seleccionar color"
                x = 600
                for i, col in enumerate(colors):
                    if x <= ix <= x + 120:
                        current_color = col
                        highlight_idx = i
                        break
                    x += 150

        # 5. Pellizco: Ajustar grosor del pincel
        elif is_pinch:
            pinch_frames += 1
            if pinch_frames >= required_frames:
                rel = 1 - (iy / float(hCam))
                new_thickness = int(min_brush + rel * (max_brush - min_brush))
                brushThickness = int(brushThickness * 0.6 + new_thickness * 0.4)
                gesture_text = f"Grosor: {brushThickness}px"

        # 6. Un dedo arriba: Dibujar
        elif index_up and total_up == 1:
            draw_frames += 1
            if draw_frames >= required_frames:
                if xp == 0 and yp == 0: xp, yp = ix, iy
                cv2.line(canvas, (xp, yp), (ix, iy), current_color, brushThickness)
                xp, yp = ix, iy
                gesture_text = "Dibujando"

    else:
        # Reset total cuando no hay mano presente
        erase_frames = select_frames = draw_frames = fist_frames = pinch_frames = 0
        gesture_text = "Esperando mano..."
        xp, yp = 0, 0

    # -------------------------------------------------------------
    # RENDERIZADO DE INTERFAZ (UI)
    # -------------------------------------------------------------
    # Indicador de color actual
    cv2.rectangle(combined, (20, 20), (180, 70), (40, 40, 40), -1)
    cv2.putText(combined, "Color:", (30, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.rectangle(combined, (130, 30), (170, 60), current_color, -1)

    # UI condicional (Paleta, Grosor, etc.)
    if palette_active: combined = draw_palette(combined, highlight_idx)
    if is_pinch: combined = draw_thickness_bar(combined, brushThickness)
    combined = draw_status_bar(combined, gesture_text)

    cv2.imshow(WINDOW_NAME, combined)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()