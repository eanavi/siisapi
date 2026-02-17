from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .base import ServicioBase
from app.componentes.siis1n.modelos.turno import Turno


class ServicioTurno(ServicioBase):
    def __init__(self):
        super().__init__(Turno, 'id_turno')

    def leer_turno_medico(self, db: Session, id_medico: int, pagina: int, tamanio: int):
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

    def leer_turno_prestacion(self, db: Session, id_prestacion: int, pagina: int, tamanio: int):
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

    def leer_turno_medico_fecha(self, db: Session, nombre_usuario: str, fecha: str):
        """
        Lee los turnos de un medico en una fecha especifica
        """
        turno = db.execute(text(f""" select * from public.fn_fechasturno(:nombre_usuario, :fecha) """), {'nombre_usuario': nombre_usuario, 'fecha': fecha})
        filas = turno.mappings().all()
        #resultado = []
        #for fila in filas:
        #    dato = dict(fila)
        #    # Mapear 'diasemana' (BD) a 'dia_semana' (Pydantic)
        #    if "diasemana" in dato:
        #        dato["dia_semana"] = dato.pop("diasemana")
        #    resultado.append(dato)
        #return resultado
        return filas
