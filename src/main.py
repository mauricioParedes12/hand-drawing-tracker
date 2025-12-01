import cv2
import numpy as np

from config import *
from utils import push_snapshot
from ui import draw_palette, draw_status_bar, draw_thickness_bar
from gestures import process_gestures
from drawing import merge_canvas

# ------------------------------
# ESTADO GLOBAL
# ------------------------------
state = {
    "stabilized_ix": None,
    "stabilized_iy": None,
}

snapshots = []
MAX_SNAPSHOTS = 25

palette_active = False
current_color = colors[0]
gesture_text = "Modo Normal"

xp, yp = 0, 0

required_frames = 4
erase_frames = 0
select_frames = 0
draw_frames = 0
fist_frames = 0
pinch_frames = 0

ix = iy = 0
total_up = 0
is_pinch = False

save_counter = 1

# ------------------------------
# WEBCAM
# ------------------------------
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

WINDOW_NAME = "HandPicture"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, wCam, hCam)

# ------------------------------
# LOOP PRINCIPAL
# ------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    img = frame.copy()

    # Reducir imagen para procesamiento
    small = cv2.resize(frame, (0, 0), fx=proc_scale, fy=proc_scale)
    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_small)

    highlight_idx = None
    is_pinch = False  

    if result.multi_hand_landmarks:

        lm = result.multi_hand_landmarks[0].landmark

        # ------------------------------
        # Procesar gestos
        # ------------------------------
        G = process_gestures(lm, canvas, state)
        ix, iy = G["ix"], G["iy"]
        up = G["up"]
        total_up = G["total_up"]
        index_up = G["index_up"]
        middle_up = G["middle_up"]
        is_pinch = G["is_pinch"]

        # Reset de contadores
        if total_up != 5: erase_frames = 0
        if not (index_up and middle_up and total_up == 2): select_frames = 0
        if not (index_up and total_up == 1): draw_frames = 0
        if total_up != 0: fist_frames = 0
        if not is_pinch: pinch_frames = 0

        # --------------------------------------------------------
        # GESTOS
        # --------------------------------------------------------

        # PUÑO (reset)
        if total_up == 0:
            fist_frames += 1
            if fist_frames >= required_frames:
                palette_active = False
                xp = yp = 0
                gesture_text = "Puño detectado"

        # BORRAR (5 dedos)
        elif total_up == 5 and not palette_active:
            erase_frames += 1
            if erase_frames >= required_frames:
                if xp == 0 and yp == 0:
                    xp, yp = ix, iy

                cv2.line(canvas, (xp, yp), (ix, iy), (0, 0, 0), eraserThickness)
                xp, yp = ix, iy
                gesture_text = "Borrando..."

        # SELECCIÓN DE COLOR
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

        # PINCH (grosor del pincel)
        elif is_pinch:
            pinch_frames += 1
            if pinch_frames >= required_frames:

                rel = 1 - (iy / float(hCam))
                new_thickness = int(min_brush + rel * (max_brush - min_brush))

                brushThickness = int(brushThickness * 0.6 + new_thickness * 0.4)
                gesture_text = f"Grosor: {brushThickness}px"

        # DIBUJAR (solo índice)
        elif index_up and total_up == 1:
            draw_frames += 1

            if draw_frames == 1:
                push_snapshot(canvas, snapshots, MAX_SNAPSHOTS)

            if draw_frames >= required_frames:
                if xp == 0 and yp == 0:
                    xp, yp = ix, iy

                cv2.line(canvas, (xp, yp), (ix, iy), current_color, brushThickness)
                xp, yp = ix, iy
                gesture_text = "Dibujando"

        else:
            gesture_text = "Modo Normal"
            xp = yp = 0

    else:
        erase_frames = select_frames = draw_frames = fist_frames = pinch_frames = 0
        gesture_text = "Esperando mano..."
        xp = yp = 0

    # ------------------------------
    # FUSIÓN CANVAS + VIDEO
    # ------------------------------
    combined = merge_canvas(img, canvas)

    # ------------------------------
    # Color actual
    # ------------------------------
    cv2.rectangle(combined, (20, 20), (180, 70), (40, 40, 40), -1)
    cv2.putText(combined, "Color:", (30, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.rectangle(combined, (130, 30), (170, 60), current_color, -1)

    # ------------------------------
    # Círculo del borrador
    # ------------------------------
    if total_up == 5 and not palette_active:
        cv2.circle(combined, (ix, iy), eraserThickness // 2, (0, 0, 0), 2)

    # ------------------------------
    # Paleta de colores
    # ------------------------------
    if palette_active:
        combined = draw_palette(combined, highlight_idx)

    # ------------------------------
    # Barra de grosor (pinch)
    # ------------------------------
    if is_pinch:
        combined = draw_thickness_bar(combined, brushThickness)

    # ------------------------------
    # Barra inferior de estado
    # ------------------------------
    combined = draw_status_bar(combined, gesture_text)

    cv2.imshow(WINDOW_NAME, combined)

    # Salir con Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
