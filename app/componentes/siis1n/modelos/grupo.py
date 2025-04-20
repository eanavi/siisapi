from sqlalchemy import Integer, String, CHAR
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from typing import List
from .base import ModeloBase, ParametroBase
from .lista import Lista


class Grupo(ParametroBase):
    __tablename__ = "grupo"

    id_grupo: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    nombre_grupo: Mapped[str] = mapped_column(String(60), nullable=False)
    tipo: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    area: Mapped[str] = mapped_column(CHAR(1), nullable=False)

    lista: Mapped[List["Lista"]] = relationship(back_populates="grupo")
