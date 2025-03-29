from sqlalchemy import Column, String, CHAR
from sqlalchemy.orm import DeclarativeBase


class ModeloBase(DeclarativeBase):
    __abstract__ = True

    estado_reg = Column(CHAR(1), default='V')
    usuario_reg = Column(String(20))
    ip_reg = Column(String(15))
