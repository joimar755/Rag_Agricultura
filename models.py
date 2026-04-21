from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, FLOAT, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)


class Cultivos(Base):
    __tablename__ = "cultivo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    tipo = Column(String, index=True)
    ubicacion = Column(String, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    userCultivo = relationship("User")

class Estaciones(Base):
    __tablename__ = "estacion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    cultivo_id = Column(Integer, ForeignKey("cultivo.id", ondelete="CASCADE"), nullable=False)
    estacionCultivo = relationship("Cultivos")

class DHT22(Base):
    __tablename__ = "dht_22"
    Temeperatura = Column(FLOAT, nullable=False)
    Huemedad = Column(FLOAT, nullable=False)
    estacion_id = Column(Integer, ForeignKey("estacion.id", ondelete="CASCADE"), nullable=False)
    estacion_dht22 = relationship("Estaciones")

class PH_Suelo(Base):
    __tablename__ = "ph_suelo"
    Ph = Column(FLOAT, nullable=False)
    estacion_id = Column(Integer, ForeignKey("estacion.id", ondelete="CASCADE"), nullable=False)
    estacion_ph = relationship("Estaciones")    

class Detecciones(Base):
    __tablename__ = "detecciones"
    nombre = Column(Text, index=True)
    cultivo_id = Column(Integer, ForeignKey("cultivo.id", ondelete="CASCADE"), nullable=False)
    detectcionCultivo = relationship("Cultivos")
    
class Recomendaciones()