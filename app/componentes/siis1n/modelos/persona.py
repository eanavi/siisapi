import uuid
from sqlalchemy import String, Date, CHAR
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import ModeloBase


class Persona(ModeloBase):
    __tablename__ = "persona"

    id_persona: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tipo: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    ci: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False)
    paterno: Mapped[Optional[str]] = mapped_column(String(60))
    materno: Mapped[Optional[str]] = mapped_column(String(60))
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    fecha_nacimiento: Mapped[Date] = mapped_column(Date, nullable=False)
    sexo: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    direccion: Mapped[Optional[dict]] = mapped_column(JSONB)
    telefono: Mapped[Optional[dict]] = mapped_column(JSONB)
    correo: Mapped[Optional[dict]] = mapped_column(JSONB)
