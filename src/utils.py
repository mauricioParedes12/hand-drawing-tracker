from config import *

def fingers_up(lm): # Función para detectar qué dedos están levantados según landmarks
    tips = [4, 8, 12, 16, 20] # indices de puntas de dedos
    fingers = [] # lista que guarda si cada dedo está arriba
    fingers.append(lm[tips[0]].x < lm[3].x) # pulgar evaluado distinto por su orientación
    for i in range(1, 5): 
        fingers.append(lm[tips[i]].y < lm[tips[i] - 2].y) # los 4 otros dedos se compara la punta con la articulación inferior
    return fingers

