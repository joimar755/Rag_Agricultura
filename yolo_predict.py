import cv2
from ultralytics import YOLO
import os
import json

# Ruta base del proyecto
base_path = os.path.dirname(os.path.abspath(__file__))

# Imagen
ruta_completa = os.path.join(base_path, "img", "Cercospora_Melonganae.jpg")

# Modelo
model = YOLO("best.pt")

# Leer imagen
img = cv2.imread(ruta_completa)

if img is None:
    print("Error: no se pudo cargar la imagen")
    exit()

# Inferencia
results = model(img, conf=0.6)

detections = []

for result in results:
    for box in result.boxes:

        # Coordenadas
        x_min, y_min, x_max, y_max = map(float, box.xyxy[0].cpu().numpy())

        # Confianza
        confidence = float(box.conf.cpu().numpy().item())

        # Clase
        class_id = int(box.cls.cpu().numpy().item())
        label = model.names[class_id]

        detections.append({
            "label": label            
        })

# Mostrar JSON
print(json.dumps(detections, indent=4))

# Imagen anotada
annotated = results[0].plot()
cv2.imshow("Detecciones", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()