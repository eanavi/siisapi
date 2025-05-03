from sqlalchemy import Integer, CHAR, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, CHAR
from .base import ParametroBase


class Lista(ParametroBase):
    __tablename__ = "lista"

    id_lista: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    id_grupo: Mapped[int] = mapped_column(
        Integer, ForeignKey('grupo.id_grupo'), nullable=False)
    cod_texto: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    cod_numero: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(120), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
