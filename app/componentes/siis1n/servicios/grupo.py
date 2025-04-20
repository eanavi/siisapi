from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .base import ServicioBase

# from typing import List
from ..modelos.grupo import Grupo
# from app.utiles.paginacion import paginacion


class ServicioGrupo(ServicioBase):
    def __init__(self):
        super().__init__(Grupo, 'id_grupo')

    def obtener_lista(self, db: Session, grupo: str):
        try:
            resultado = db.execute(text(f"""
            SELECT public.obtener_lista_por_grupo(:criterio);
                                        """), {'criterio': grupo})
            return resultado.mappings().all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error en la consulta de la base de datos: {str(e)}")


'''
    def leer_grupo(self, db: Session, pagina: int = 1, tamanio: int = 10) -> List[Grupo]:
        try:
            db_grupos = db.execute(text(""" select g.id_grupo, g.nombre_grupo, g.tipo, 
                                        g.area, g.estado_reg from grupo g where estado_reg = 'V'"""
                                        ))
            grupos = db_grupos.mappings().all()
            return paginacion(grupos, pagina, tamanio)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al leer los grupos: {str(e)}")
'''
