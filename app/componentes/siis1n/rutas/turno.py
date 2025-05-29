from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.turno import ServicioTurno
from app.componentes.siis1n.esquemas.turno import TurnoResponse, RespuestaPaginada, TurnoCreate
from app.nucleo.seguridad import verificar_token
from app.nucleo.baseDatos import leer_bd

serv_turno = ServicioTurno()

router = APIRouter(prefix="/turnos", tags=["Turno"])


@router.get("/", response_model=RespuestaPaginada,
            summary=f"Listar todos los turnos",
            description=f"Lista todos los turnos registrados en el sistema")
def listar_turnos(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description=f"Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description=f"Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    turnos = serv_turno.leer_todos(db, pagina, tamanio)
    return turnos


@router.get("/{id_turno}",
            response_model=TurnoResponse,
            summary=f"Obtener el detalle de un turno",
            description=f"Obtiene los detalles de un turno registrado en el sistema")
def obtener_turno(id_turno: int, db: Session = Depends(leer_bd)):
    turno = serv_turno.leer(db, id_turno)
    return turno


@router.post("/",
             response_model=TurnoResponse,
             summary="Registrar un Turno",
             description="Registra un nuevo turno en el sistema"
             )
def crear_turno(
        turno: TurnoCreate,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    turno_creado = serv_turno.crear(
        db=db,
        obj=turno.model_dump(),
        usuario_reg=usuario,
        ip_reg=ip)
    return turno_creado


@router.put("/{id_turno}",
            response_model=TurnoResponse,
            summary=f"Actualizar un Turno",
            description=f"Actualiza los datos de un turno registrado en el sistema")
def actualizar_turno(
        id_turno: int,
        turno: TurnoCreate,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    turno_actualizado = serv_turno.actualizar(
        db=db,
        id_obj=id_turno,
        obj=turno.model_dump(),
        usuario_mod=usuario,
        ip_mod=ip)
    return turno_actualizado


@router.delete("/{id_turno}",
               response_model=bool,
               summary="Eliminar un Turno",
               description="Elimina un turno registrado en el sistema")
def eliminar_turno(
        id_turno: int,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    resultado = serv_turno.eliminar(
        db=db,
        id=id_turno,
        usuario_mod=usuario,
        ip_mod=ip)
    return resultado


@router.get("/medico/{id_medico}",
            response_model=RespuestaPaginada,
            summary=f"Listar todos los turnos de un medico",
            description=f"Lista todos los turnos registrados en el sistema")
def listar_turnos_medico(
    id_medico: int,
    pagina: int = Query(1, alias="pagina", ge=1,
                        description=f"Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description=f"Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    turnos = serv_turno.leer_turno_medico(db, id_medico, pagina, tamanio)
    return turnos


@router.get("/prestacion/{id_prestacion}",
            response_model=RespuestaPaginada,
            summary=f"Listar todos los turnos de una prestacion",
            description=f"Lista todos los turnos registrados en el sistema")
def listar_turnos_prestacion(
        id_prestacion: int,
        pagina: int = Query(1, alias="pagina", ge=1,
                            description=f"Numero de pagina a mostrar"),
        tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                             description=f"Cantidad de registros a mostrar"),
        db: Session = Depends(leer_bd)):
    turnos = serv_turno.leer_turno_prestacion(
        db, id_prestacion, pagina, tamanio)
    return turnos
