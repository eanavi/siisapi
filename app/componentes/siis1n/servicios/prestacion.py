from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import Optional
from fastapi import HTTPException, status
from .base import ServicioBase
from app.componentes.siis1n.modelos.prestacion import Prestacion
from ..esquemas.prestacion import PrestacionLista


class ServicioPrestacion(ServicioBase):
    def __init__(self):
        super().__init__(Prestacion, 'id_prestacion')

    def leer_por_tipo_perfil(self, db: Session, id_empleado: int):
        try:
            consulta = db.execute(text(f"""
                select p.id_prestacion, p.nombre_prestacion, p.sigla 
	            from prestacion as p 
		        inner join usuario u on p.id_rol = u.id_rol 
                where u.id_empleado = :id_empleado"""), {'id_empleado': id_empleado})
            resultados = consulta.mappings().all()
            if not resultados:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron prestaciones para el tipo de perfil proporcionado.")

            return [PrestacionLista.from_orm(fila) for fila in resultados]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al leer las prestaciones por tipo de perfil: {str(e)}")
    
    def crear_prestacion(self, db: Session, obj: dict,
                           usuario_reg: Optional[str] = None,
                           ip_reg: Optional[str] = None) -> Prestacion:
        return self.crear(db, obj, usuario_reg, ip_reg)
    

