from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.componentes.siis1n.esquemas.empleado import EmpleadoPersona
from app.componentes.siis1n.servicios.persona import ServicioPersona
from app.componentes.siis1n.modelos.base import ParametroBase, ModeloBase
from fastapi import HTTPException, status
from typing import Optional
from .base import ServicioBase
from ..modelos.empleado import Empleado


class ServicioEmpleado(ServicioBase):
    def __init__(self):
        super().__init__(Empleado, 'id_empleado')

    def leer_empleados(self, db:Session, criterio:str = None):
        try:
            empleados = db.execute(text(f"""
            select * from public.buscar_empleados(:criterio)                            
            """), {"criterio":criterio})
            filas = empleados.all()

            if not filas:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No se encontraron empleados")
            return filas
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al obtener empleados {str(e)}")

    def crear_empleado_con_persona(
            self,
            db: Session,
            empleado_persona: EmpleadoPersona,
            id_centro: int,
            usuario_reg: Optional[str] = None,
            ip_reg: Optional[str] = None
    ) -> Empleado:
        try:
            if isinstance(empleado_persona, dict):
                empleado_persona = EmpleadoPersona(**empleado_persona)

            datos_persona = empleado_persona.model_dump(
                exclude={"tipo_empleado", "profesion", "registro_profesional", "id_centro", "cargo"})
            # Crear la persona

            nueva_persona = ServicioPersona().crear(db, datos_persona, usuario_reg, ip_reg)

            # Crear el empleado
            datos_empleados = {
                "id_persona": nueva_persona.id_persona,
                "id_centro": id_centro,
                "tipo_empleado": empleado_persona.tipo_empleado,
                "profesion": empleado_persona.profesion,
                "registro_profesional": empleado_persona.registro_profesional,
                "cargo": empleado_persona.cargo,
            }
            nuevo_empleado = self.crear(
                db, datos_empleados, usuario_reg, ip_reg)
            return nuevo_empleado
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al crear el empleado: {str(e)}")

    def leer_empleado_con_persona(self, db: Session, id_empleado: int) -> EmpleadoPersona:
        try:
            empleado = self.leer(db, id_empleado)
            if not empleado:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Empleado no encontrado")
            persona = ServicioPersona().leer(db, empleado.id_persona)
            if not persona:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Empleado no encontrada")
            empleado_persona = {
                "id_persona": empleado.id_persona,
                "id_centro": empleado.id_centro,
                "tipo_empleado": empleado.tipo_empleado,
                "profesion": empleado.profesion,
                "registro_profesional": empleado.registro_profesional,
                "cargo": empleado.cargo,
                "tipo": persona.tipo,
                "ci": persona.ci,
                "paterno": persona.paterno,
                "materno": persona.materno,
                "nombres": persona.nombres,
                "fecha_nacimiento": persona.fecha_nacimiento,
                "sexo": persona.sexo,
                "direccion": persona.direccion,
                "telefono": persona.telefono,
                "correo": persona.correo,
            }
            return empleado_persona
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al obtener el empleado: {str(e)}")

    def actualizar_empleado_con_persona(self, db: Session, id_empleado: int, empleado_persona: EmpleadoPersona) -> EmpleadoPersona:
        try:
            empleado = self.leer(db, id_empleado)
            if not empleado:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Empleado no encontrado")
            # Actualizar la persona
            datos_persona = empleado_persona.model_dump(
                exclude={"tipo_empleado", "profesion", "registro_profesional", "id_centro", "cargo"})
            persona_actualizada = ServicioPersona().actualizar(
                db, empleado.id_persona, datos_persona)

            # Actualizar el empleado
            datos_empleado = {
                "id_centro": empleado_persona.id_centro,
                "tipo_empleado": empleado_persona.tipo_empleado,
                "profesion": empleado_persona.profesion,
                "registro_profesional": empleado_persona.registro_profesional,
                "cargo": empleado_persona.cargo,
            }
            empleado_actualizado = self.actualizar(
                db, id_empleado, datos_empleado)
            empleado_persona_act = {
                "id_persona": empleado_actualizado.id_persona,
                "id_centro": empleado_actualizado.id_centro,
                "tipo_empleado": empleado_actualizado.tipo_empleado,
                "profesion": empleado_actualizado.profesion,
                "registro_profesional": empleado_actualizado.registro_profesional,
                "cargo": empleado_actualizado.cargo,
                "tipo": persona_actualizada.tipo,
                "ci": persona_actualizada.ci,
                "paterno": persona_actualizada.paterno,
                "materno": persona_actualizada.materno,
                "nombres": persona_actualizada.nombres,
                "fecha_nacimiento": persona_actualizada.fecha_nacimiento,
                "sexo": persona_actualizada.sexo,
                "direccion": persona_actualizada.direccion,
                "telefono": persona_actualizada.telefono,
                "correo": persona_actualizada.correo,
            }
            return empleado_persona_act
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al actualizar el empleado: {str(e)}")
