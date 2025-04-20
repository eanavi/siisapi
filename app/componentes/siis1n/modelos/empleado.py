from sqlalchemy import ForeignKey, Integer, CHAR, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from typing import Optional, List, TYPE_CHECKING
from .base import ModeloBase


if TYPE_CHECKING:
    from .persona import Persona
    from .centro import Centro
    from .usuario import Usuario


class Empleado(ModeloBase):
    __tablename__ = "empleado"

    id_empleado: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    id_persona: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey('persona.id_persona'), nullable=False)
    id_centro: Mapped[int] = mapped_column(
        Integer, ForeignKey('centro.id_centro'), nullable=False)
    tipo_empleado: Mapped[str] = mapped_column(
        CHAR(1), nullable=False, default="A")
    profesion: Mapped[int] = mapped_column(Integer, nullable=False)
    registro_profesional: Mapped[Optional[str]] = mapped_column(String(20))
    cargo: Mapped[str] = mapped_column(String(120), nullable=False)

    persona: Mapped["Persona"] = relationship()  # Relación unidireccional
    centro: Mapped["Centro"] = relationship(back_populates="empleados")
    usuarios: Mapped[List["Usuario"]] = relationship(back_populates="empleado")
