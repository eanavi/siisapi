from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import ModeloBase


class Usuario(ModeloBase):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    id_empleado: Mapped[int] = mapped_column(
        Integer, ForeignKey("empleado.id_empleado"), nullable=False)
    id_rol: Mapped[int] = mapped_column(
        Integer, ForeignKey("rol.id_rol"), nullable=False)
    nombre_usuario: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True)
    clave: Mapped[str] = mapped_column(String(255), nullable=False)
