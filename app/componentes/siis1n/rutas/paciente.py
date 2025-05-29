from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.paciente import ServicioPaciente
from app.componentes.siis1n.esquemas.paciente import RespuestaPaginada, \
    PacientePersona, PacienteListado
from app.nucleo.seguridad import verificar_token
from app.nucleo.conexion import obtener_id_centro
from app.nucleo.baseDatos import leer_bd

serv_paciente = ServicioPaciente()

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.get("/", response_model=RespuestaPaginada, summary="Listar todas los Pacientes",
            description="Lista todas los pacientes registrados en el sistema")
def listar_pacientes(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description="Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    pacientes = serv_paciente.leer_todos(db, pagina, tamanio)
    return pacientes

@router.get("/asignados", response_model=list[PacienteListado])
def listar_pacientes_asignados(
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    """
    Lista los pacientes asignados al usuario autenticado.
    """
    nombre_usuario = token["nombre_usuario"]
    pacientes = serv_paciente.leer_pacientes_asignados(
        db, nombre_usuario)
    return pacientes


@router.get("/{id_paciente}", response_model=PacientePersona,
            summary="Obtener Paciente por ID",
            description="Obtiene un paciente por su ID")
def obtener_paciente(id_paciente: int, db: Session = Depends(leer_bd)):
    paciente = serv_paciente.leer_paciente_con_persona(db, id_paciente)
    return paciente





@router.post("/", response_model=int,
             summary="Registrar un nuevo Paciente",
             description="Registra un nuevo paciente en el sistema")
def crear_paciente(
        paciente_persona: PacientePersona,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token),
        id_centro: int = Depends(obtener_id_centro)):
    ip = request.client.host
    usuario = token["nombre_usuario"]
    paciente = serv_paciente.crear_paciente_con_persona(
        db,
        paciente_persona.model_dump(),
        id_centro=id_centro,
        usuario_reg=usuario,
        ip_reg=ip
    )
    return paciente.id_paciente


@router.put("/{id_paciente}", response_model=PacientePersona,
            summary="Actualizar Paciente",
            description="Actualiza un paciente por su ID")
def actualizar_paciente(id_paciente: int, paciente_persona: PacientePersona,
                        db: Session = Depends(leer_bd)):
    paciente = serv_paciente.actualizar_paciente_con_persona(
        db, id_paciente, paciente_persona)
    return paciente


@router.delete("/{id_paciente}",
               response_model=PacientePersona,
               summary="Eliminar Paciente",
               description="Elimina un paciente por su ID")
def eliminar_paciente(
        id_paciente: int,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    paciente = serv_paciente.eliminar(
        db,
        id=id_paciente,
        usuario_reg=usuario,
        ip_reg=ip,
    )
    return paciente
