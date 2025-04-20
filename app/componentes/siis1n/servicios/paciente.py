from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.componentes.siis1n.esquemas.paciente import PacientePersona
from app.componentes.siis1n.servicios.persona import ServicioPersona
from fastapi import HTTPException, status
from .base import ServicioBase
from ..modelos.paciente import Paciente


class ServicioPaciente(ServicioBase):
    def __init__(self):
        super().__init__(Paciente, "id_paciente")

    def crear_paciente_con_persona(
            self,
            db: Session,
            paciente_persona: PacientePersona) -> Paciente:
        try:
            datos_persona = paciente_persona.model_dump(
                exclude={"id_persona", "id_centro",
                         "estado_civil", "ocupacion",
                         "nivel_estudios", "mun_nacimiento",
                         "mun_residencia", "idioma_hablado", "idioma_materno",
                         "autopertenencia", "gestion_comunitaria"})
            # Crear la persona
            datos_persona["tipo"] = "P"  # Paciente
            nueva_persona = ServicioPersona().crear(db, datos_persona)

            # Crear el paciente
            datos_paciente = {
                "id_persona": nueva_persona.id_persona,
                "id_centro": paciente_persona.id_centro,
                "estado_civil": paciente_persona.estado_civil,
                "ocupacion": paciente_persona.ocupacion,
                "nivel_estudios": paciente_persona.nivel_estudios,
                "mun_nacimiento": paciente_persona.mun_nacimiento,
                "mun_residencia": paciente_persona.mun_residencia,
                "idioma_hablado": paciente_persona.idioma_hablado,
                "idioma_materno": paciente_persona.idioma_materno,
                "autopertenencia": paciente_persona.autopertenencia,
                "gestion_comunitaria": paciente_persona.gestion_comunitaria,
            }
            nuevo_paciente = self.crear(db, datos_paciente)
            return nuevo_paciente
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al crear el paciente: {str(e)}")

    """
    Lee un paciente y la persona asociada en la base de datos.
    """

    def leer_paciente_con_persona(
            self, db: Session,
            id_paciente: int) -> PacientePersona:
        try:
            paciente = self.leer(db, id_paciente)
            if not paciente:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Paciente no encontrado")
            persona = ServicioPersona().leer(db, paciente.id_persona)
            if not persona:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Paciente no encontrada")
            paciente_persona = {
                "id_persona": paciente.id_persona,
                "id_centro": paciente.id_centro,
                "estado_civil": paciente.estado_civil,
                "ocupacion": paciente.ocupacion,
                "nivel_estudios": paciente.nivel_estudios,
                "mun_nacimiento": paciente.mun_nacimiento,
                "mun_residencia": paciente.mun_residencia,
                "idioma_hablado": paciente.idioma_hablado,
                "idioma_materno": paciente.idioma_materno,
                "autopertenencia": paciente.autopertenencia,
                "gestion_comunitaria": paciente.gestion_comunitaria,
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
            return paciente_persona
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al obtener el paciente: {str(e)}")

    """
    Actualiza un paciente y la persona asociada en la base de datos.
    """

    def actualizar_paciente_con_persona(
            self,
            db: Session,
            id_persona: int,
            paciente_persona: PacientePersona) -> PacientePersona:
        try:
            paciente = self.leer(db, id_persona)
            if not paciente:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Paciente no encontrado")
            # Actualizar la persona
            datos_persona = paciente_persona.model_dump(
                exclude={"id_persona", "id_centro",
                         "estado_civil", "ocupacion",
                         "nivel_estudios", "mun_nacimiento",
                         "mun_residencia", "idioma_hablado", "idioma_materno",
                         "autopertenencia", "gestion_comunitaria"})
            ServicioPersona().actualizar(db, paciente.id_persona, datos_persona)

            # Actualizar el paciente
            datos_paciente = {
                "id_centro": paciente_persona.id_centro,
                "estado_civil": paciente_persona.estado_civil,
                "ocupacion": paciente_persona.ocupacion,
                "nivel_estudios": paciente_persona.nivel_estudios,
                "mun_nacimiento": paciente_persona.mun_nacimiento,
                "mun_residencia": paciente_persona.mun_residencia,
                "idioma_hablado": paciente_persona.idioma_hablado,
                "idioma_materno": paciente_persona.idioma_materno,
                "autopertenencia": paciente_persona.autopertenencia,
                "gestion_comunitaria": paciente_persona.gestion_comunitaria,
            }
            self.actualizar(db, id_persona, datos_paciente)
            return paciente_persona
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al actualizar el empleado: {str(e)}")
