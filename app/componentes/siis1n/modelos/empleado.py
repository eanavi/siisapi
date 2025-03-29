from sqlalchemy import Column, Integer, String, CHAR, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from .base import ModeloBase


class Empleado(ModeloBase):
    __tablename__ = 'empleado'

    id_empleado = Column(Integer, primary_key=True,
                         autoincrement=True, index=True)
    id_persona = Column(PGUUID(as_uuid=True), ForeignKey(
        'persona.id_persona'), nullable=False)
    id_centro = Column(Integer, ForeignKey('centro.id_centro'), nullable=False)
    # A: Administrativo, M: Medico
    tipo_empleado = Column(CHAR(1), nullable=False, default='A')
    profesion = Column(Integer, nullable=False)
    registro_profesional = Column(String(20), nullable=True)
    cargo = Column(String(120), nullable=False)

    persona = relationship('Persona', back_populates='empleado')
    centro = relationship('Centro', back_populates='empleados')
    usuarios = relationship('Usuario', back_populates='empleado')
