from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from .base import ServicioBase
from ..modelos.menu import Menu
from app.componentes.siis1n.esquemas.usuario import InformacionUsuario



class ServicioMenu(ServicioBase):
    def __init__(self):
        super().__init__(Menu, 'id_menu')



    def obtener_menus_por_rol(self, db: Session, rol:str):
        try:
            resultado = db.execute(
                text("""SELECT * FROM public.fn_obtener_menu_por_rol(:nombre_rol)"""),
                {'nombre_rol': rol}
            )
            filas = [dict(fila) for fila in resultado.mappings().all()]
            return filas
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al leer los menus: {str(e)}"
            )

    def obtener_menus_por_usuario(self, db: Session, usuario:str):
        try:
            resultado = db.execute(
                text("""SELECT * FROM public.fn_obtener_menu_por_usuario(:nombre_usuario)"""),
                {'nombre_usuario': usuario}
            )
            filas = [dict(fila) for fila in resultado.mappings().all()]
            return filas
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al leer los menus: {str(e)}"
            )

