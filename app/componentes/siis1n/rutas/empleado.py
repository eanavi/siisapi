from fastapi import APIRouter, Depends,  Query, Request
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.empleado import ServicioEmpleado
from app.componentes.siis1n.esquemas.empleado import RespuestaPaginada, \
    EmpleadoPersona, EmpleadoResponse
from app.nucleo.seguridad import verificar_token
from app.nucleo.conexion import obtener_id_centro
from app.nucleo.baseDatos import leer_bd

serv_empleado = ServicioEmpleado()

router = APIRouter(prefix="/empleados", tags=["Empleados"])


@router.get("/", response_model=RespuestaPaginada, summary="Listar todas los Empleados",
            description="Lista todas los empleados registrados en el sistema")
def listar_personas(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description="Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    empleados = serv_empleado.leer_todos(db, pagina, tamanio)
    return empleados


@router.get("/{id_empleado}", response_model=EmpleadoPersona,
            summary="Obtener Empleado por ID",
            description="Obtiene un empleado por su ID")
def obtener_empleado(id_empleado: int, db: Session = Depends(leer_bd)):
    empleado = serv_empleado.leer_empleado_con_persona(db, id_empleado)
    return empleado


@router.post("/", response_model=EmpleadoResponse,
             summary="Registrar un nuevo Empleado",
             description="Registra un nuevo empleado en el sistema")
def crear_empleado(
        empleado_persona: EmpleadoPersona,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token),
        id_centro: int = Depends(obtener_id_centro)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    empleado = serv_empleado.crear_empleado_con_persona(
        db,
        empleado_persona.model_dump(),
        id_centro=id_centro,
        usuario_reg=usuario,
        ip_reg=ip)
    return empleado


@router.put("/{id_empleado}", response_model=EmpleadoPersona,
            summary="Actualizar Empleado",
            description="Actualiza un empleado por su ID")
def actualizar_empleado(id_empleado: int, empleado_persona: EmpleadoPersona,
                        db: Session = Depends(leer_bd)):
    empleado = serv_empleado.actualizar_empleado_con_persona(
        db, id_empleado, empleado_persona)
    return empleado


@router.delete("/{id_empleado}",
               response_model=bool,
               summary=f"Eliminar un empleado",
               description=f"Elimina un empleado de forma logica\
                  registrado en el sistema")
def eliminar_empleado(
        id_empleado: int,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    resultado = serv_empleado.eliminar(
        db,
        id=id_empleado,
        usuario_reg=usuario,
        ip_reg=ip)
    return resultado
