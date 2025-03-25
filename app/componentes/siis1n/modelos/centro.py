from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from .base import ModeloBase


class Centro(ModeloBase):
    __tablename__ = 'centro'

    id_centro = Column(Integer, primary_key=True, autoincrement=True, index=True)
    codigo_snis = Column(Integer, nullable=False, unique=True)
    nombre = Column(String(120), nullable=False)
    direccion = Column(String(120), nullable=True)
    usuario = Column(String(20), nullable=False)
    clave = Column(String(255), nullable=False)
    puerto = Column(Integer, nullable=False)

    empleados = relationship("Empleado", back_populates="centro")
