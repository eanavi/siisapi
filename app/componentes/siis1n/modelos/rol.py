from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import ModeloBase


class Rol(ModeloBase):
    __tablename__ = 'rol'

    id_rol = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String(60), nullable=False)
    descripcion = Column(String(120), nullable=True)

    usuarios = relationship('Usuario', back_populates='rol')
