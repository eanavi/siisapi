from sqlalchemy import Integer, String, CHAR, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from .base import ModeloBase
from .persona import Persona
from .centro import Centro


class Paciente(ModeloBase):
    __tablename__ = "paciente"

    id_paciente: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    id_persona: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey('persona.id_persona'), nullable=False)
    id_centro: Mapped[int] = mapped_column(
        Integer, ForeignKey('centro.id_centro'), nullable=False)
    estado_civil: Mapped[str] = mapped_column(
        CHAR(2), nullable=True, default="SO")
    ocupacion: Mapped[Optional[int]] = mapped_column(Integer)
    nivel_estudios: Mapped[Optional[int]] = mapped_column(Integer)
    mun_nacimiento: Mapped[int] = mapped_column(Integer, nullable=False)
    mun_residencia: Mapped[int] = mapped_column(Integer, nullable=False)
    idioma_hablado: Mapped[int] = mapped_column(Integer, nullable=False)
    idioma_materno: Mapped[int] = mapped_column(Integer, nullable=False)
    autopertenencia: Mapped[int] = mapped_column(Integer, nullable=False)
    gestion_comunitaria: Mapped[Optional[str]] = mapped_column(String(120))

    persona: Mapped["Persona"] = relationship()
    centro: Mapped["Centro"] = relationship()
