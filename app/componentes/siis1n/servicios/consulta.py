from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import text, select
from fastapi import HTTPException, status
from ..modelos.usuario import Usuario
from .base import ServicioBase
from ..modelos.reserva import Reserva
from ..modelos.turno import Turno
from ..modelos.consulta import Consulta
from ..esquemas.consulta import ConsultaEnfermeria, ConsultaBase

class ServicioConsulta(ServicioBase):
    def __init__(self):
        super().__init__(Consulta, 'id_consulta')
    
    def crear_consulta_enfermeria(
        self, 
        db, 
        consulta_enf: ConsultaEnfermeria, 
        id_reserva: int, 
        id_paciente: int,
        usuario_reg: Optional[str] = None,
        ip_reg: Optional[str] = None
        ) -> Consulta:

        try:

            datos_consulta: Dict[str, Any] = consulta_enf.model_dump(exclude_unset=True)
            datos_finales: Dict[str, Any] = ConsultaBase(
                id_reserva=id_reserva,
                fecha = datetime.now(),
            ).model_dump(by_alias=True)

            datos_finales.update(datos_consulta)



            stmt = select(Usuario.id_empleado).where(Usuario.nombre_usuario == usuario_reg)
            id_enfermera = db.execute(stmt).scalar()

            stmt = select(Turno.id_medico).join(Reserva, Turno.id_turno == Reserva.id_turno).where(Reserva.id_reserva == id_reserva)
            id_medico = db.execute(stmt).scalar()   

            datos_finales['id_reserva'] = id_reserva
            datos_finales['usuario_reg'] = usuario_reg
            datos_finales['ip_reg'] = ip_reg
            datos_finales['fecha'] = datetime.now() # Fecha y hora de la creación de la consulta (si esta es la intención)
            # Asumo que 'fecha_reg' es la columna para el registro de la transacción
            datos_finales['fecha_reg'] = datetime.now() 
            datos_finales['id_enfermera'] = id_enfermera
            datos_finales['id_medico'] = id_medico


            nueva_consulta = self.crear(db, datos_finales)
            return nueva_consulta
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al crear la consulta: {str(e)}")


