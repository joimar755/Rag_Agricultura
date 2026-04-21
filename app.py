from typing import Optional

from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from models import Cultivos, Estaciones, LecturaSensores, RecomendacionesRag
import models
from database import engine , SessionLocal
from sqlalchemy.orm import Session
import cv2
import numpy as np
from ultralytics import YOLO
from io import BytesIO
from starlette.responses import JSONResponse



class Ph(BaseModel):
    temperatura: float
    humedad: float
    humedad_suelo: float
    estacion_id: Optional[int] = None
    

class cultivo(BaseModel):
    nombre: str
    tipo: str
    ubicacion: str
   

class cultivoCreate(cultivo):
    pass 

    class Config:
       orm_mode = True


class detecciones(BaseModel):
    nombre: str
    cultivo_id: int
 
class estacion(BaseModel):
    nombre: str
    cultivo_id: int
    
class recomendacion(BaseModel): 
    pregunta: str
    respuestas:str
    cultivo_id: int
    


models.Base.metadata.create_all(bind=engine)
#models.Base.metadata.drop_all(bind=engine)


app = FastAPI()


yolo_model = YOLO("best.pt")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


""" @app.post("/sensor-data")
async def receive_data(data: Ph , db: Session = Depends(get_db)):
    print(f" Temp: {data.temperatura}°C  Hum: {data.humedad}% suelo:{data.humedad_suelo}")
    # Aquí puedes guardar en BD, publicar a MQTT, etc.
    return {"status": "ok", "received": data.dict()}  """

@app.post("/cultivo")
async def create_cultivo(cultivo: cultivoCreate, db: Session = Depends(get_db)):
    existe = db.query(Cultivos).filter(Cultivos.nombre == cultivo.nombre).first()
    if existe is None:
        db_cultivo = Cultivos(nombre=cultivo.nombre, tipo=cultivo.tipo, ubicacion=cultivo.ubicacion)
        db.add(db_cultivo)
        db.commit()
        db.refresh(db_cultivo)
    else:
        raise HTTPException(
            status_code=404, detail="cultivo with this name already exists"
        )
    return {"data": db_cultivo}

@app.post("/estacion")
async def create_cultivo(estaciones: estacion, db: Session = Depends(get_db)):
    cultivo_existe = db.query(Cultivos).filter(Cultivos.id == estaciones.cultivo_id).first()
    if not cultivo_existe:
        raise HTTPException(status_code=404, detail="Cultivo no existe")
    
    existe = db.query(Estaciones).filter(Estaciones.nombre == estaciones.nombre).first()
    if existe is None:
        db_estacion = Estaciones(nombre=estaciones.nombre , cultivo_id = estaciones.cultivo_id)
        db.add(db_estacion)
        db.commit()
        db.refresh(db_estacion)
    else:
        raise HTTPException(
            status_code=404, detail="cultivo with this name already exists"
        )
    return {"data": db_estacion}

@app.post("/sensor-data")
async def create_cultivo(data: Ph, db: Session = Depends(get_db)):
        estacion_id = data.estacion_id

        if estacion_id is None:
             estacion = db.query(Estaciones).first()
             estacion_id = estacion.id
        else:
            raise HTTPException(status_code=404, detail="estacion no existe")

        db_lectura = LecturaSensores(temperatura = data.temperatura , humedad= data.humedad, Ph = data.humedad_suelo, estacion_id = estacion_id)
        db.add(db_lectura)
        db.commit()
        db.refresh(db_lectura)
        
        return {"data": db_lectura}
    
@app.post("/detect/")
async def detect_objects(file: UploadFile = File(...)):
    # Read image file
    image_bytes = await file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Run YOLO model
    results = yolo_model(image)
    detections = []
    
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            detections.append({
                "label": yolo_model.names[class_id],
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2]
            })
    
    return JSONResponse(content={"detections": detections})