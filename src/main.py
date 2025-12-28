import cv2
import numpy as np
import os

from config import *
from ui import draw_spatial_menu, draw_status_bar, draw_thickness_bar, draw_save_progress
from gestures import process_gestures
from drawing import merge_canvas

# -------------------------------------------------------------
# FUNCIÓN PARA GUARDAR EL DIBUJO CON FONDO BLANCO
# -------------------------------------------------------------
def save_canvas(canvas, counter):
    # Generamos un fondo blanco para reemplazar el fondo negro del canvas
    white_bg = np.ones_like(canvas) * 255

    # Procesamos máscaras para transferir solo el dibujo al fondo blanco
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    # Combinamos fondo blanco y trazos de color
    bg = cv2.bitwise_and(white_bg, white_bg, mask=mask_inv)
    fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    final = cv2.add(bg, fg)

    # Exportamos la imagen a la carpeta de destino
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
xp, yp = 0, 0 

# Contadores para validar que un gesto sea intencional y no un error
required_frames = 4
erase_frames = select_frames = draw_frames = fist_frames = pinch_frames = 0
save_frames = 0
SAVE_REQUIRED_FRAMES = 40 
save_counter = 1

# -------------------------------------------------------------
# CONFIGURACIÓN DE VIDEO
# -------------------------------------------------------------
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

WINDOW_NAME = "HandPicture"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow(WINDOW_NAME, wCam, hCam)
total_up = 0
ix, iy = 0, 0

# -------------------------------------------------------------
# LOOP PRINCIPAL
# -------------------------------------------------------------
while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1) 
    img = frame.copy()

    # Redimensionamos la imagen para que MediaPipe trabaje más rápido
    small = cv2.resize(frame, (0, 0), fx=proc_scale, fy=proc_scale)
    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_small)

    highlight_idx = None
    is_pinch = False
    
    # Combinamos la cámara con el lienzo de dibujo
    combined = merge_canvas(img, canvas)  

    if result.multi_hand_landmarks:
        lm = result.multi_hand_landmarks[0].landmark

        # Obtenemos la interpretación de la mano desde gestures.py
        G = process_gestures(lm, canvas, state)
        ix, iy, up, total_up = G["ix"], G["iy"], G["up"], G["total_up"]
        index_up, middle_up, is_pinch = G["index_up"], G["middle_up"], G["is_pinch"]

        # Limpieza de contadores si se deja de hacer un gesto
        if total_up != 5: erase_frames = 0
        if not (index_up and middle_up and total_up == 2): select_frames = 0
        if not (index_up and total_up == 1): draw_frames = 0
        if total_up != 0: fist_frames = 0
        if not is_pinch: pinch_frames = 0

        # LÓGICA DE GESTOS
        # 1. Guardar: se activa con el gesto de "cuernos"
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

        # 2. Mano cerrada: desactiva menús y resetea trazo
        if total_up == 0:
            fist_frames += 1
            if fist_frames >= required_frames:
                palette_active = False
                xp = yp = 0
                gesture_text = "Mano cerrada"

        # 3. Mano abierta: activa el borrador (pinta negro sobre el canvas)
        elif total_up == 5 and not palette_active:
            erase_frames += 1
            if erase_frames >= required_frames:
                if xp == 0 and yp == 0: xp, yp = ix, iy
                cv2.line(canvas, (xp, yp), (ix, iy), (0, 0, 0), eraserThickness)
                xp, yp = ix, iy
                gesture_text = "Borrando..."

        # 4. Dos dedos arriba: activa la selección de color espacial
        elif index_up and middle_up and total_up == 2:
            select_frames += 1
            if select_frames >= required_frames:
                palette_active = True
                gesture_text = "Seleccione un color"

        # 5. Pellizco: ajusta el tamaño del pincel según la altura de la mano
        elif is_pinch:
            pinch_frames += 1
            if pinch_frames >= required_frames:
                rel = 1 - (iy / float(hCam))
                new_thickness = int(min_brush + rel * (max_brush - min_brush))
                brushThickness = int(brushThickness * 0.6 + new_thickness * 0.4)
                gesture_text = f"Grosor: {brushThickness}px"

        # 6. Un dedo arriba: modo dibujo estándar
        elif index_up and total_up == 1:
            draw_frames += 1
            # Dibujamos un cursor visual del pincel
            cv2.circle(combined, (ix, iy), brushThickness // 2, current_color, -1)
            cv2.circle(combined, (ix, iy), (brushThickness // 2) + 2, (255, 255, 255), 1)
            if draw_frames >= required_frames:
                if xp == 0 and yp == 0: xp, yp = ix, iy
                cv2.line(canvas, (xp, yp), (ix, iy), current_color, brushThickness)
                xp, yp = ix, iy
                gesture_text = "Dibujando"

    else:
        # Reset de variables si no se detecta ninguna mano
        erase_frames = select_frames = draw_frames = fist_frames = pinch_frames = 0
        gesture_text = "Esperando mano..."
        xp, yp = 0, 0

    # -------------------------------------------------------------
    # RENDERIZADO DE INTERFAZ (UI)
    # -------------------------------------------------------------
    if palette_active: 
        combined, detected_color_idx = draw_spatial_menu(combined, ix, iy)
        if detected_color_idx is not None:
            current_color = colors[detected_color_idx]
            
    if is_pinch: combined = draw_thickness_bar(combined, brushThickness)
    
    # Mostramos la barra de estado y el cursor del borrador si aplica
    combined = draw_status_bar(combined, gesture_text, current_color)
    if total_up == 5 and not palette_active:
        cv2.circle(combined, (ix, iy), eraserThickness // 2, (0, 0, 0), 2)

    cv2.imshow(WINDOW_NAME, combined)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()