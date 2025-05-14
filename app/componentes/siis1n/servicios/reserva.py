from .base import ServicioBase
from app.componentes.siis1n.modelos.reserva import Reserva


class ServicioReserva(ServicioBase):
    def __init__(self):
        super().__init__(Reserva, 'id_reserva')

    def leer_reserva_turno(self, db, id_turno: int, pagina: int, tamanio: int):
        """
        Lee las reservas de un turno especifico
        """
        query = db.query(Reserva).filter(Reserva.id_turno == id_turno)
        total = query.count()
        reservas = query.offset((pagina - 1) * tamanio).limit(tamanio).all()
        return {
            "total": total,
            "pagina": pagina,
            "tamanio": tamanio,
            "reservas": reservas
        }

    def leer_reserva_paciente(self, db, id_paciente: int, pagina: int, tamanio: int):
        """
        Lee las reservas de un paciente especifico
        """
        query = db.query(Reserva).filter(Reserva.id_paciente == id_paciente)
        total = query.count()
        reservas = query.offset((pagina - 1) * tamanio).limit(tamanio).all()
        return {
            "total": total,
            "pagina": pagina,
            "tamanio": tamanio,
            "reservas": reservas
        }
