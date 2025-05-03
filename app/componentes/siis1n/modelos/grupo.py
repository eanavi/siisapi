from sqlalchemy import Integer, String, CHAR
from sqlalchemy.orm import Mapped, mapped_column

from .base import ParametroBase


class Grupo(ParametroBase):
    __tablename__ = "grupo"

    id_grupo: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    nombre_grupo: Mapped[str] = mapped_column(String(60), nullable=False)
    tipo: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    area: Mapped[str] = mapped_column(CHAR(1), nullable=False)
