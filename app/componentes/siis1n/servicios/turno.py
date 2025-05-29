from .base import ServicioBase
from app.componentes.siis1n.modelos.turno import Turno


class ServicioTurno(ServicioBase):
    def __init__(self):
        super().__init__(Turno, 'id_turno')

    def leer_turno_medico(db, id_medico: int, pagina: int, tamanio: int):
        """
        Lee los turnos de un medico especifico
        """
        query = db.query(Turno).filter(Turno.id_medico == id_medico)
        total = query.count()
        turnos = query.offset((pagina - 1) * tamanio).limit(tamanio).all()
        return {
            "total": total,
            "pagina": pagina,
            "tamanio": tamanio,
            "turnos": turnos
        }

    def leer_turno_prestacion(db, id_prestacion: int, pagina: int, tamanio: int):
        """
        Lee los turnos de una prestacion especifica
        """
        query = db.query(Turno).filter(Turno.id_prestacion == id_prestacion)
        total = query.count()
        turnos = query.offset((pagina - 1) * tamanio).limit(tamanio).all()
        return {
            "total": total,
            "pagina": pagina,
            "tamanio": tamanio,
            "turnos": turnos
        }
