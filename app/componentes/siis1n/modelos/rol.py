from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING

from .base import ModeloBase

if TYPE_CHECKING:
    from .rol_menu import RolMenu

class Rol(ModeloBase):
    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    nombre_rol: Mapped[str] = mapped_column(String(60), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(120))

    # Relación con RolMenu
    menu_rel: Mapped[list["RolMenu"]] = relationship(
        "RolMenu",
        back_populates="rol"  # Esto debe coincidir con la propiedad en RolMenu
    )

#from .rol_menu import RolMenu