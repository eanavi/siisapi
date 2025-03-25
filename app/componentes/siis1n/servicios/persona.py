from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .base import ServicioBase
from ..modelos.persona import Persona
from app.utiles.paginacion import paginacion

class ServicioPersona(ServicioBase):
    def __init__(self):
        super().__init__(Persona, 'id_persona')

    def buscar_persona(self, db: Session, criterio: str, pagina: int, tamanio: int):
        resultado = db.execute(text(f"""
            SELECT * FROM public.buscar_personas(:criterio)
        """), {'criterio': criterio})
        filas = resultado.fetchall()
        resultado = [dict(fila._mapping) for fila in filas]
        return paginacion(resultado, pagina, tamanio)