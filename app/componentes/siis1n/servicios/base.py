from datetime import datetime
from sqlalchemy.orm import Session, DeclarativeBase
from typing import List, TypeVar, Generic, Union, Optional
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.componentes.siis1n.modelos.base import ModeloBase, ParametroBase
from app.utiles.paginacion import paginacion
from sqlalchemy.orm import joinedload

T = TypeVar("T", bound=DeclarativeBase)


class ServicioBase(Generic[T]):
    def __init__(self, modelo: type[T], id_column: str):
        self.modelo = modelo
        self.id_column = id_column

    def crear(
            self,
            db: Session,
            obj: dict,
            usuario_reg: Optional[str] = None,
            ip_reg: Optional[str] = None,
            relaciones: Optional[List[str]] = None
    ) -> T:
        try:
            nuevo_obj = self.modelo(**obj)

            if isinstance(nuevo_obj, ModeloBase):
                if usuario_reg:
                    nuevo_obj.usuario_reg = usuario_reg
                if ip_reg:
                    nuevo_obj.ip_reg = ip_reg
                nuevo_obj.estado_reg = 'V'  # Vigente
                nuevo_obj.fecha_reg = datetime.now()
            db.add(nuevo_obj)
            db.commit()
            if relaciones:
                db.refresh(nuevo_obj, attribute_names=relaciones)
            else:
                db.refresh(nuevo_obj)
            return nuevo_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al crear el objeto: {str(e)}")

    def leer(self, db: Session, id: Union[int, UUID]) -> T:
        try:
            db_obj = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column) == id,
                self.modelo.estado_reg == 'V'
            ).first()
            if not db_obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Objeto no encontrado")
            return db_obj
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al leer el objeto: {str(e)}")

    def leer_todos(
            self,
            db: Session,
            pagina: int = 1,
            tamanio: int = 10,
            filtros: Optional[dict] = None,
            relaciones: Optional[List[str]] = None
    ) -> List[T]:
        try:
            query = db.query(self.modelo).filter(self.modelo.estado_reg == 'V')

            # Aplicar filtros personalizados
            if filtros:
                for campo, valor in filtros.items():
                    query = query.filter(getattr(self.modelo, campo) == valor)

            # Cargar relaciones opcionales
            if relaciones:
                for relacion in relaciones:
                    query = query.options(joinedload(relacion))

            db_objs = query.all()
            return paginacion(db_objs, pagina, tamanio)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al leer los objetos: {str(e)}")

    def actualizar(self, db: Session, id: Union[int, UUID], obj: dict) -> T:
        try:
            db_obj = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column) == id,
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

    def eliminar(
            self,
            db: Session,
            id: Union[int, UUID],
            usuario_reg: Optional[str] = None,
            ip_reg: Optional[str] = None
    ) -> bool:
        try:
            db_obj = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column) == id,
                self.modelo.estado_reg == 'V'
            ).first()
            if not db_obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Objeto no encontrado")
            if isinstance(db_obj, ModeloBase):
                if usuario_reg:
                    db_obj.usuario_reg = usuario_reg
                if ip_reg:
                    db_obj.ip_reg = ip_reg
                db_obj.estado_reg = 'A'  # Anulado
            if isinstance(db_obj, ParametroBase):
                db_obj.estado_reg = 'A'
            db.commit()
            db.refresh(db_obj)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al eliminar el objeto: {str(e)}")

    def eliminar_fisico(self, db: Session, id: Union[int, UUID], usuario_reg: Optional[str] = None, ip_reg: Optional[str] = None) -> bool:
        try:
            db_obj = db.query(self.modelo).filter(
                getattr(self.modelo, self.id_column) == id
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
