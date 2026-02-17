from sqlalchemy import Integer, String, CHAR, ForeignKey, DateTime, DECIMAL, TEXT
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import ModeloBase


class Consulta(ModeloBase):
    __tablename__ = "consulta"

    id_consulta: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    id_reserva: Mapped[int] = mapped_column(
        Integer, ForeignKey('reserva.id_reserva'), nullable=False)
    id_medico: Mapped[int] = mapped_column(
        Integer, ForeignKey('empleado.id_empleado'), nullable=False)
    id_enfermera: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('empleado.id_empleado'), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    peso: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 2), nullable=True)
    talla: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 2), nullable=True)
    temperatura: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(4, 2), nullable=True)
    presion: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    frecuencia_cardiaca: Mapped[Optional[int]
                                ] = mapped_column(Integer, nullable=True)
    frecuencia_respiratoria: Mapped[Optional[int]
                                    ] = mapped_column(Integer, nullable=True)
    saturacion: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(4, 2), nullable=True)
    inyectables: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sueros: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    curaciones: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    otras_enf: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    motivo: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    ex_fisico: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    diagnostico: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    tratamiento: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    dx_cie10: Mapped[list[Optional[str]]] = mapped_column(
        ARRAY(String(10)), nullable=True)
    mortalidad: Mapped[Optional[str]] = mapped_column(CHAR(1), nullable=True)
    referencia: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    subsidio: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
