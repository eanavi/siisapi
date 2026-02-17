from sqlalchemy import Column, Integer, Date, Time, String, ForeignKey, CheckConstraint, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.componentes.siis1n.modelos.base import ModeloBase


class Reserva(ModeloBase):
    __tablename__ = 'reserva'

    id_reserva: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    id_turno: Mapped[int] = mapped_column(
        Integer, ForeignKey('public.turno.id_turno'), nullable=False)
    id_paciente: Mapped[int] = mapped_column(
        Integer, ForeignKey('paciente.id_paciente'))
    fecha_reserva: Mapped[Date] = mapped_column(Date)
    hora_reserva: Mapped[Time] = mapped_column(Time)

    # No definimos las relaciones aqui

    def __repr__(self):
        return f"<Reserva(id={self.id}, turno_id={self.turno_id}, \
        paciente_id={self.paciente_id}, fecha_reserva={self.fecha_reserva}, \
            hora_reserva={self.hora_reserva}, estado='{self.estado}')>"
