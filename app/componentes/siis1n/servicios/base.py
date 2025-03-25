from sqlalchemy.orm import Session, DeclarativeBase
from typing import List, Type, TypeVar, Generic, Union
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.utiles.paginacion import paginacion

T = TypeVar("T", bound=DeclarativeBase)

class ServicioBase(Generic[T]):
    def __init__(self, modelo:type[T], id_column:str):
        self.modelo = modelo
        self.id_column = id_column
    
    def crear(self, db:Session, obj:dict) -> T:
        try:
            nuevo_obj = self.modelo(**obj)
            db.add(nuevo_obj)
            db.commit()
            db.refresh(nuevo_obj)
            return nuevo_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"Error al crear el objeto: {str(e)}")
    
    def leer(self, db:Session, id:Union[int,UUID]) -> T:
        try:
            query = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column)==id,
                self.modelo.estado_reg == 'V'
                )
            db_obj = db.query(self.modelo).first()
            if not db_obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail=f"Objeto no encontrado")
            return db_obj
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error al leer el objeto: {str(e)}")

    def leer_todos(self, db:Session, pagina:int=1, tamanio:int=10) -> List[T]:
        try:
            db_objs = db.query(self.modelo).filter(
                self.modelo.estado_reg == 'V'
                ).all()
            return paginacion(db_objs, pagina, tamanio)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"Error al leer los objetos: {str(e)}")
    
    def actualizar(self, db:Session, id:Union[int,UUID], obj:dict) -> T:
        try:
            db_obj = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column)==id,
                self.modelo.estado_reg == 'V'
                ).first()
            if not db_obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail=f"Objeto no encontrado")
            for key, value in obj.items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"Error al actualizar el objeto: {str(e)}")
    
    def eliminar(self, db:Session, id:Union[int,UUID]) -> bool:
        try:
            db_obj = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column)==id,
                self.modelo.estado_reg == 'V'
                ).first()
            if not db_obj:  
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail=f"Objeto no encontrado")
            db_obj.estado_reg = 'A' # Anulado
            db.commit()
            db.refresh(db_obj)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"Error al eliminar el objeto: {str(e)}")
    
    def eliminar_fisico(self, db:Session, id:Union[int,UUID]) -> bool:
        try:
            db_obj = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column)==id
                ).first()
            if not db_obj:  
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail=f"Objeto no encontrado")
            db.delete(db_obj)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"Error al eliminar el objeto: {str(e)}")