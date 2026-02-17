from enum import Enum as PyEnum
from sqlalchemy import Integer, Date, Time, String, ForeignKey, CheckConstraint, ARRAY, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.componentes.siis1n.modelos.base import ModeloBase

class DiaSemana(PyEnum):
    L = 'L'
    M = 'M'
    I = 'I'
    J = 'J'
    V = 'V'
    S = 'S'
    D = 'D'



class Turno(ModeloBase):
    __tablename__ = 'turno'

    id_turno: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    id_medico: Mapped[int] = mapped_column(Integer, ForeignKey(
        'empleado.id_empleado'))  # Asumiendo una tabla de empleados
    id_prestacion: Mapped[int] = mapped_column(Integer, ForeignKey(
        'prestacion.id_prestacion'))  # Asumiendo una tabla de servicios
    fecha_inicio: Mapped[Date] = mapped_column(Date)
    fecha_final: Mapped[Date] = mapped_column(Date)
    hora_inicio: Mapped[Time] = mapped_column(Time)
    hora_final: Mapped[Time] = mapped_column(Time)
    dia_semana: Mapped[list[DiaSemana]] = mapped_column(
        ARRAY(Enum(
            DiaSemana, 
            name='dia_semana_enum', 
            # Asegúrate de especificar el esquema si no es el por defecto
            schema='public', 
            values_callable=lambda x: [e.value for e in x]
        ))
    )
    #dia_semana: Mapped[list[DiaSemana]] = mapped_column(
    #    ARRAY(Enum(DiaSemana, 'dia_semana_enum', values_callable=lambda x: [e.value for e in x]))
    #)



    __table_args__ = (
        CheckConstraint('fecha_final >= fecha_inicio', name='check_fechas'),
        CheckConstraint('hora_final > hora_inicio', name='check_horas'), {'schema':'public'},
    )

    def __repr__(self):
        return f"<Turno(id={self.id_turno}, id_medico={self.id_medico}, \
        fecha_inicio={self.fecha_inicio}, fecha_final={self.fecha_final}, \
        hora_inicio={self.hora_inicio}, hora_final={self.hora_final}, \
        dia_semana={self.dia_semana})>"
