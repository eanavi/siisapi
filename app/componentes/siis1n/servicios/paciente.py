from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.componentes.siis1n.esquemas.paciente import PacientePersona
from app.componentes.siis1n.servicios.persona import ServicioPersona
from app.utiles.varios import es_menor_de_un_anio, generar_codigo_rn
from fastapi import HTTPException, status
from datetime import date
from .base import ServicioBase
from ..modelos.paciente import Paciente
from ..modelos.persona import Persona


class ServicioPaciente(ServicioBase):
    def __init__(self):
        super().__init__(Paciente, "id_paciente")

    def leer_pacientes(self, db:Session, criterio:str = None):
        try:
            personas = db.execute(text(f"""
            select * from public.buscar_pacientes(:criterio)
            """), {"criterio":criterio})

            filas = personas.all()
            if not filas:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No se encontraron pacientes")
            return filas
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"Error al obtener pacientes asignados : {str(e)}")

    def buscar_paciente(self, db: Session, ci: str) -> PacientePersona:
        try:
            # Usamos .all() para verificar si hay duplicidad con el patrón de búsqueda
            resultados = db.query(Persona, Paciente).\
                join(Paciente, Persona.id_persona == Paciente.id_persona).\
                filter(Persona.ci.ilike(f"%{ci}%")).all()

            if not resultados:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No se encontró ningún paciente con el CI: {ci}"
                )

            if len(resultados) > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Búsqueda ambigua: {len(resultados)} coincidencias encontradas. Sea más específico."
                )

            # Extraemos la única tupla (Persona, Paciente)
            persona_db, paciente_db = resultados[0]

            # Combinamos los atributos. Pydantic filtrará los campos extra de SQLAlchemy
            return PacientePersona(
                **{**persona_db.__dict__, **paciente_db.__dict__}
            )

        except SQLAlchemyError as e:
            db.rollback() # Buena práctica ante errores de sesión
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al consultar la base de datos"
            )

    def leer_pacientes_paginados(self, db: Session, pagina: int,  tamanio: int,  criterio: str | None = None):
        try:
            # Calcular offset (registro inicial)
            offset = (pagina - 1) * tamanio

            # Ejecutar el procedimiento almacenado con paginación
            query = text("""
                SELECT * FROM public.buscar_pacientes(:criterio, :p_limit, :p_offset)
            """)

            params = {
                "criterio": criterio,
                "p_limit": tamanio,
                "p_offset": offset
            }

            result = db.execute(query, params)
            filas = result.mappings().all()

            if not filas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontraron pacientes"
                )

            return {
                "total": filas[0]['total_count'],
                "pagina": pagina,
                "tamanio": tamanio,
                "items": filas
            }

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener pacientes paginados: {str(e)}"
            )

    def crear_paciente_con_persona(
            self,
            db: Session,
            paciente_persona: PacientePersona,
            id_centro: int,
            usuario_reg: str | None = None,
            ip_reg: str | None = None
    ) -> Paciente:
        try:
            if isinstance(paciente_persona, dict):
                paciente_persona = PacientePersona(**paciente_persona)
            
            menor_de_un_anio = es_menor_de_un_anio(paciente_persona.fecha_nacimiento)

            if not paciente_persona.ci and not menor_de_un_anio:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El Carnet de identidad es obligatorio para pacientes mayores de un año"
                )

            datos_persona = paciente_persona.model_dump(
                exclude={"id_persona", "id_centro",
                         "estado_civil", "ocupacion", "tipo_sangre",
                         "nivel_estudios", "mun_nacimiento",
                         "mun_residencia", "idioma_hablado", "idioma_materno",
                         "autopertenencia", "gestion_comunitaria"})
            # Crear la persona
            datos_persona["tipo"] = "P"  # Paciente

            if menor_de_un_anio and not paciente_persona.ci:
                datos_persona["ci"] = generar_codigo_rn(id_centro)

            nueva_persona = ServicioPersona().crear(db, datos_persona, usuario_reg, ip_reg)

            # Crear el paciente
            datos_paciente = {
                "id_persona": nueva_persona.id_persona,
                "id_centro": id_centro,
                "estado_civil": paciente_persona.estado_civil,
                "tipo_sangre": paciente_persona.tipo_sangre,
                "ocupacion": paciente_persona.ocupacion,
                "nivel_estudios": paciente_persona.nivel_estudios,
                "idioma_hablado": paciente_persona.idioma_hablado,
                "idioma_materno": paciente_persona.idioma_materno,
                "autopertenencia": paciente_persona.autopertenencia,
                "gestion_comunitaria": paciente_persona.gestion_comunitaria,
            }
            nuevo_paciente = self.crear(
                db, datos_paciente, usuario_reg, ip_reg)
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
                "tipo_sangre": paciente.tipo_sangre,
                "ocupacion": paciente.ocupacion,
                "nivel_estudios": paciente.nivel_estudios,
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
            id_centro: int,
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
                "id_centro": id_centro,
                "estado_civil": paciente_persona.estado_civil,
                "tipo_sangre": paciente_persona.tipo_sangre,
                "ocupacion": paciente_persona.ocupacion,
                "nivel_estudios": paciente_persona.nivel_estudios,
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


                                
    def buscar_pacientes_asignados(self, db: Session, nombre_usuario: str, criterio: str):
        """
        Busca los pacientes asignados al usuario autenticado.
        """
        hoy = date.today().strftime("%Y-%m-%d")
        try:

            pacientes = db.execute(text(f""" select * from public.buscar_pacientes_por_usuario(:nombre_usuario, :criterio, :fecha)"""),
                                  {'nombre_usuario': nombre_usuario,
                                   'criterio': criterio,
                                   'fecha': hoy})
                                   
            filas = pacientes.mappings().all()
            if not filas:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No se encontraron pacientes asignados")
            return filas
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error al buscar los pacientes asignados: {str(e)}")                           
    
    def buscar_pacientes_enf_asignados(self, db: Session, nombre_usuario: str, criterio: str):
        """
        Busca los pacientes asignados al usuario de enfermeria autenticado.
        """
        hoy = date.today().strftime("%Y-%m-%d")
        try:
            pacientes = db.execute(text(f""" select * from public.buscar_pacientes_enf_por_usuario(:nombre_usuario, :criterio, :fecha)"""),
            {'nombre_usuario': nombre_usuario,
            'criterio': criterio,
            'fecha': hoy})
            filas = pacientes.mappings().all()
            if not filas:
                raise HTTPException(status_code=status.HTTP_4, 
                                    detail="No se encontraron pacientes asignados")
            return filas
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar los pacientes asignados: {str(e)}")