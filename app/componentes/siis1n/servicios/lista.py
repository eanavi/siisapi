from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.utiles.paginacion import paginacion
from .base import ServicioBase
from ..modelos.lista import Lista


class ServicioLista(ServicioBase):
    def __init__(self):
        super().__init__(Lista, 'id_lista')

    def obtener_lista_por_grupo(self, db: Session, grupo: str):
        try:
            resultado = db.execute(text(
                """select * from public.obtener_lista_por_grupo(:criterio)"""), {'criterio': grupo})
            filas = [{"codigo": fila["codigo"], "descripcion": fila["descripcion"]}
                     for fila in resultado.mappings().all()]
            return filas
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al leer la lista: {str(e)}")
