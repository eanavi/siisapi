from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import ParametroBase


class Menu(ParametroBase):
    __tablename__ = "menu"

    id_menu: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    id_menu_padre: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("menu.id_menu"), nullable=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    ruta: Mapped[str] = mapped_column(String(255), nullable=False)
    icono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False,
                                           default="menu")
