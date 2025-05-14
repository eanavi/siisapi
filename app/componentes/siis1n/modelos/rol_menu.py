# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from .base import ModeloBase
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .menu import Menu
    from .rol import Rol

class RolMenu(ModeloBase):
    __tablename__ = "rol_menu"

    id_rol_menu: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    id_rol: Mapped[int] = mapped_column(
        Integer, ForeignKey("rol.id_rol"), nullable=False)
    id_menu: Mapped[int] = mapped_column(
        Integer, ForeignKey("menu.id_menu"), nullable=False)
    metodo: Mapped[list[str]] = mapped_column(ARRAY(String))

    # Relación con Menu
    menu: Mapped["Menu"] = relationship(
        "Menu",
        back_populates="rol_rel"  # Esto debe coincidir con la propiedad en Menu
    )

    # Relación con Rol
    rol: Mapped["Rol"] = relationship(
        "Rol",
        back_populates="menu_rel"  # Esto debe coincidir con la propiedad en Rol
    )


#from .menu import Menu
#from .rol import Rol
