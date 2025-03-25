import uuid
from sqlalchemy import Column, String, Date, JSON, CHAR
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from .base import ModeloBase

class Persona(ModeloBase):
    __tablename__ = 'persona'

    id_persona = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tipo = Column(CHAR(1), nullable=False)
    ci = Column(String(20), unique=True, index=True)
    paterno = Column(String(60), nullable=True)
    materno = Column(String(60), nullable=True)
    nombres = Column(String(120), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(CHAR(1), nullable=False)
    direccion = Column(JSON)
    telefono = Column(JSON)
    correo = Column(JSON)

    empleados = relationship("Empleado", back_populates="persona")

from .empleado import Empleado 
