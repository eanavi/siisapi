from sqlalchemy.orm import Session, DeclarativeBase
from typing import Type, TypeVar, Generic, List
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.utiles.paginacion import paginacion


T = TypeVar("T", bound=DeclarativeBase)


class ServBase(Generic[T]):
    def __init__(self, modelo: Type[T], id_column: int):
        self.modelo = modelo
        self.id_column = id_column

    def crear(self, db: Session, obj: dict) -> T:
        try:
            nuevo_obj = self.modelo(**obj)
            db.add(nuevo_obj)
            db.commit()
            db.refresh(nuevo_obj)
            return nuevo_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Eror al crear el objeto: {str(e)}")

    def leer(self, db: Session, id: int) -> T:
        try:
            db_obj = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column) == id
            ).first()
            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Objeto no encontrado")
            return db_obj
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al leer el objeto: {str(e)}")

    def leer_todos(self, db: Session, pagina: int = 1, tamanio: int = 10) -> List[T]:
        try:
            if hasattr(self.modelo, "HCL_ESTADO"):
                consulta = db.query(self.modelo).filter(
                    self.modelo.HCL_ESTADO == "A")
            db_ojbs = consulta.all()
            return paginacion(db_ojbs, pagina, tamanio)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al leer objetos: {str(e)}")

    def actualizar(self, db: Session, id: int, obj: dict) -> T:
        try:
            query = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column) == id)

            if hasattr(self.modelo, "HCL_ESTADO"):
                query = query.filter(self.modelo.HCL_ESTADO == 'A')

            db_obj = query.first()

            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"Objeto no encontrado")

            for clave, valor in obj.items():
                setattr(db_obj, clave, valor)

            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al actualizar el objeto: {str(e)}")

    def eliminar(self, db: Session, id: int) -> bool:
        try:
            consulta = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column) == id)

            if hasattr(self.modelo, "HCL_ESTADO"):
                consulta = consulta.filter(self.modelo.HCL_ESTADO == "A")

            db_obj = consulta.first()

            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Objeto no encontrado")
            db_obj.HCL_ESTADO = 'E'  # Eliminado
            db.commit()
            db.refresh(db_obj)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al eliminar objeto: {str(e)}")

    def eliminar_fisico(self, db: Session, id: int) -> bool:
        try:
            consulta = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column) == id)

            if hasattr(self.modelo, "HCL_ESTADO"):
                consulta = consulta.filter(self.modelo.HCL_ESTADO == "A")

            db_obj = consulta.first()

            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Objeto no encontrado")

            db.delete(db_obj)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al eliminar el objeto: {str(e)}")
