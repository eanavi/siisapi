from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING

from .base import ModeloBase


if TYPE_CHECKING:
    from .usuario import Usuario


class Rol(ModeloBase):
    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    nombre: Mapped[str] = mapped_column(String(60), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(120))
