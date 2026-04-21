from fastapi import FastAPI
from pydantic import BaseModel
from . import models
from .database import engine , SessionLocal


class dht22(BaseModel):
    temperatura: float
    humedad: float

class Ph(dht22):
    humedad_suelo: float





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
async def receive_data(data: Ph):
    print(f" Temp: {data.temperatura}°C  Hum: {data.humedad}% suelo:{data.humedad_suelo}")
    # Aquí puedes guardar en BD, publicar a MQTT, etc.
    return {"status": "ok", "received": data.dict()}