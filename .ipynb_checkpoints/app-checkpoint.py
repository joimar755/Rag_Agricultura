from fastapi import FastAPI
from pydantic import BaseModel


class dht22(BaseModel):
    temperatura: float
    humedad: float



app = FastAPI()


@app.post("/sensor-data")
async def receive_data(data: dht22):
    print(f" Temp: {data.temperatura}°C  Hum: {data.humedad}%")
    # Aquí puedes guardar en BD, publicar a MQTT, etc.
    return {"status": "ok", "received": data.dict()}