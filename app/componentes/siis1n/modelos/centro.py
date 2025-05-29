from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import ModeloBase


class Centro(ModeloBase):
    __tablename__ = "centro"

    id_centro: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    codigo_snis: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True)
    nombre_centro: Mapped[str] = mapped_column(String(120), nullable=False)
    direccion: Mapped[Optional[str]] = mapped_column(String(120))
    usuario: Mapped[str] = mapped_column(String(20), nullable=False)
    clave: Mapped[str] = mapped_column(String(255), nullable=False)
    puerto: Mapped[int] = mapped_column(Integer, nullable=False)
