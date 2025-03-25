from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import ModeloBase


class Usuario(ModeloBase):
    __tablename__ = "usuario"
 
    id_usuario = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre_usuario = Column(String(20), nullable=False)
    id_empleado = Column(Integer, ForeignKey('empleado.id_empleado'))
    clave = Column(String(255), nullable=False)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"), nullable=False)

    #relaciones
    empleado = relationship("Empleado", back_populates="usuarios")
    rol = relationship("Rol", back_populates="usuarios")

# Importación tardía para evitar importaciones circulares
from .empleado import Empleado
from .rol import Rol
