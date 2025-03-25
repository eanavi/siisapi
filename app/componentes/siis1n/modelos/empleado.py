from sqlalchemy import Column, Integer, String, ForeignKey, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base import ModeloBase

class Empleado(ModeloBase):
    __tablename__ = "empleado"

    id_empleado = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_persona = Column(PG_UUID(as_uuid=True), ForeignKey("persona.id_persona"), nullable=False)
    tipo = Column(CHAR(1), default='A') # A = 'Area Administrtiva', M='Area Medica'
    profesion = Column(Integer, nullable=False)
    registro_profesional = Column(String(20), nullable=True)
    id_centro = Column(Integer, ForeignKey("centro.id_centro"), nullable=False)
    cargo = Column(String(120), nullable=True)

    #relaciones
    usuarios = relationship("Usuario", back_populates="empleado")
    persona = relationship("Persona", back_populates="empleados")
    centro = relationship("Centro", back_populates="empleados")

from .persona import Persona
from .usuario import Usuario
from .centro import Centro
