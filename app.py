from fastapi import FastAPI, Depends
from pydantic import BaseModel
from . import models
from .database import engine , SessionLocal
from sqlalchemy.orm import Session



class dht22(BaseModel):
    temperatura: float
    humedad: float

class Ph(dht22):
    humedad_suelo: float

class usuarios(BaseModel):
    username: str
    password: str

class cultivo(BaseModel):
    nombre: str
    tipo: str
    ubicacion: str
   

class cultivoCreate(cultivo):
    pass 

class cultivo_base(cultivo):
    id: int
    usuario_id: int
    
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


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/sensor-data")
async def receive_data(data: Ph , db: Session = Depends(get_db)):
    print(f" Temp: {data.temperatura}°C  Hum: {data.humedad}% suelo:{data.humedad_suelo}")
    # Aquí puedes guardar en BD, publicar a MQTT, etc.
    return {"status": "ok", "received": data.dict()}