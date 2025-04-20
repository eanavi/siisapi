from sqlalchemy import String, CHAR, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class ModeloBase(DeclarativeBase):
    __abstract__ = True

    estado_reg: Mapped[str] = mapped_column(CHAR(1), default='V')
    usuario_reg: Mapped[str] = mapped_column(String(20))
    ip_reg: Mapped[str] = mapped_column(String(15))
    fecha_reg: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)


class ParametroBase(DeclarativeBase):
    __abstract__ = True
    estado_reg: Mapped[str] = mapped_column(CHAR(1), default='V')
