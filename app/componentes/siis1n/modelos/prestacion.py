from sqlalchemy import Integer, String, CHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.componentes.siis1n.modelos.edad_sqla import TipoEdad
from app.componentes.siis1n.modelos.edad import Edad
from typing import Optional
from .base import ModeloBase


class Prestacion(ModeloBase):
    __tablename__ = "prestacion"

    id_prestacion: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    id_centro: Mapped[int] = mapped_column(
        Integer, ForeignKey('centro.id_centro'), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    sigla: Mapped[str] = mapped_column(String(10), nullable=False)
    edad_maxima: Mapped[Edad] = mapped_column(TipoEdad)
    edad_minima: Mapped[Edad] = mapped_column(TipoEdad)
    genero: Mapped[Optional[str]] = mapped_column(CHAR(1), nullable=True)
    tipo_prestador: Mapped[Optional[str]] = mapped_column(
        CHAR(1), nullable=True)
    tiempo_maximo: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)
