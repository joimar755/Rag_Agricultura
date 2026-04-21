from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, FLOAT, Text, TIMESTAMP, text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False, server_default=text('now()'))



class Cultivos(Base):
    __tablename__ = "cultivo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    tipo = Column(String, index=True)
    ubicacion = Column(String, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False, server_default=text('now()'))

    #userCultivo = relationship("User")

class Estaciones(Base):
    __tablename__ = "estacion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    cultivo_id = Column(Integer, ForeignKey("cultivo.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False, server_default=text('now()'))

    #estacionCultivo = relationship("Cultivos")

class LecturaSensores(Base):
    __tablename__ = "lectura"
    id = Column(Integer, primary_key=True, index=True)
    temperatura = Column(FLOAT, nullable=False)
    humedad = Column(FLOAT, nullable=False)
    Ph = Column(FLOAT, nullable=False)

    estacion_id = Column(Integer, ForeignKey("estacion.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False, server_default=text('now()'))

    #estacion_dht22 = relationship("Estaciones")
  
class Detecciones(Base):
    __tablename__ = "detecciones"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(Text, index=True)
    cultivo_id = Column(Integer, ForeignKey("cultivo.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False, server_default=text('now()'))

    #deteccionCultivo = relationship("Cultivos")
    
class RecomendacionesRag(Base): 
    __tablename__ = "recomendaciones"
    id = Column(Integer, primary_key=True, index=True)
    pregunta = Column(Text, index=True)
    respuestas = Column(Text, index=True)
    cultivo_id = Column(Integer, ForeignKey("cultivo.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False, server_default=text('now()'))


