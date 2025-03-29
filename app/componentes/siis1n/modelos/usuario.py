from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import ModeloBase


class Usuario(ModeloBase):
    __tablename__ = 'usuario'

    id_usuario = Column(Integer, primary_key=True,
                        autoincrement=True, index=True)
    id_empleado = Column(Integer, ForeignKey(
        'empleado.id_empleado'), nullable=False)
    id_rol = Column(Integer, ForeignKey('rol.id_rol'), nullable=False)
    nombre_usuario = Column(String(20), nullable=False)
    clave = Column(String(255), nullable=False)

    empleado = relationship('Empleado', back_populates='usuarios')
    rol = relationship('Rol', back_populates='usuarios')
