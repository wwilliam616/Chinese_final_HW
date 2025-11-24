import cv2
import numpy as np
import os
import unicodedata

# --------------------------------------
# Configuración inicial
# --------------------------------------

drawing = False
last_x, last_y = None, None

canvas = np.ones((450, 400), np.uint8) * 255

READY_BUTTON_POS = (10, 410, 150, 440)
GUIDE_BUTTON_POS = (160, 410, 350, 440)

guide_enabled = True  # guía mostrada por defecto

# --------------------------------------
# Umbral de similitud (modificable)
# --------------------------------------
# Este es el apartado donde se define cuán parecido debe ser el dibujo para considerarlo correcto
SIMILARITY_THRESHOLD = 0.20  # empieza en 0.40, se puede modificar luego

# --------------------------------------
# Cargar imagen guía
# --------------------------------------

def load_guide():
    if os.path.exists("guide.png"):
        img = cv2.imread("guide.png", cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (400, 400))
        return img
    else:
        print("⚠️ No se encontró guide.png")
        return None

guide_img = load_guide()

# --------------------------------------
# Función de dibujo
# --------------------------------------

def draw(event, x, y, flags, param):
    global drawing, last_x, last_y, guide_enabled

    # Click en botón READY
    if event == cv2.EVENT_LBUTTONDOWN:
        if READY_BUTTON_POS[0] <= x <= READY_BUTTON_POS[2] and READY_BUTTON_POS[1] <= y <= READY_BUTTON_POS[3]:
            analyze_character()
            return

        # Click en botón SHOW/HIDE
        if GUIDE_BUTTON_POS[0] <= x <= GUIDE_BUTTON_POS[2] and GUIDE_BUTTON_POS[1] <= y <= GUIDE_BUTTON_POS[3]:
            guide_enabled = not guide_enabled
            return

        drawing = True
        last_x, last_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        if y < READY_BUTTON_POS[1]:
            cv2.line(canvas, (last_x, last_y), (x, y), 0, 15)
            last_x, last_y = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False


cv2.namedWindow("Character Checker")
cv2.setMouseCallback("Character Checker", draw)

# --------------------------------------
# Cargar plantillas
# --------------------------------------

def load_templates(path="templates"):
    templates = {}
    for file in os.listdir(path):
        if file.endswith(".png"):
            ch = file.split(".")[0]
            img = cv2.imread(os.path.join(path, file), cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (200, 200))
            templates[ch] = img
    return templates

templates = load_templates()

# --------------------------------------
# Verificar si es caracter tradicional
# --------------------------------------

def is_traditional(ch):
    try:
        name = unicodedata.name(ch)
    except:
        return False
    return "CJK UNIFIED IDEOGRAPH" in name

# --------------------------------------
# Comparar con plantillas
# --------------------------------------

def most_similar_character(drawing_img):
    best_char = None
    best_score = -1

    drawing_resized = cv2.resize(drawing_img, (200, 200))

    for ch, templ in templates.items():
        res = cv2.matchTemplate(drawing_resized, templ, cv2.TM_CCOEFF_NORMED)
        score = res[0][0]

        if score > best_score:
            best_score = score
            best_char = ch

    return best_char, best_score

# --------------------------------------
# Analizar caracter dibujado
# --------------------------------------

def analyze_character():
    drawing_area = canvas[0:400, 0:400]
    char, score = most_similar_character(drawing_area)

    print(f"\nCarácter detectado: {char}")
    print(f"Similitud: {score:.2f}")

    # --------------------------------------
    # Apartado del umbral de similitud
    # --------------------------------------
    if score > SIMILARITY_THRESHOLD and is_traditional(char):
        print("✔️ Carácter correcto")
        show_result("✔️ CORRECTO", 200)
    else:
        print("❌ Carácter incorrecto")
        show_result("❌ INCORRECTO", 0)

    canvas[:] = 255

# --------------------------------------
# Mostrar resultado temporal
# --------------------------------------

def show_result(text, color_value):
    temp = canvas.copy()
    cv2.putText(temp, text, (40, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.8, color_value, 4)
    cv2.imshow("Character Checker", temp)
    cv2.waitKey(1000)

# --------------------------------------
# Bucle principal
# --------------------------------------

print("Dibuja un carácter y usa READY para analizar. SHOW/HIDE para mostrar u ocultar guía.")

while True:
    display = canvas.copy()

    # Si la guía está activada
    if guide_enabled and guide_img is not None:
        display[0:400, 0:400] = guide_img

    # Botón READY
    cv2.rectangle(display, (READY_BUTTON_POS[0], READY_BUTTON_POS[1]),
                             (READY_BUTTON_POS[2], READY_BUTTON_POS[3]),
                             200, -1)
    cv2.putText(display, "READY", (20, 435), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 2)

    # Botón SHOW / HIDE GUIDE
    cv2.rectangle(display, (GUIDE_BUTTON_POS[0], GUIDE_BUTTON_POS[1]),
                             (GUIDE_BUTTON_POS[2], GUIDE_BUTTON_POS[3]),
                             180, -1)
    label = "HIDE GUIDE" if guide_enabled else "SHOW GUIDE"
    cv2.putText(display, label, (GUIDE_BUTTON_POS[0] + 5, 435),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 2)

    cv2.imshow("Character Checker", display)
    key = cv2.waitKey(1)

    if key == ord('q'):
        break

cv2.destroyAllWindows()
