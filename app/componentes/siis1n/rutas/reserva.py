from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime
from app.componentes.siis1n.servicios.reserva import ServicioReserva
from app.componentes.siis1n.modelos.reserva import Reserva
from app.componentes.siis1n.esquemas.reserva import ReservaResponse, RespuestaPaginada, ReservaCreate
from app.nucleo.seguridad import verificar_token
from app.nucleo.baseDatos import leer_bd


serv_reserva = ServicioReserva()

router = APIRouter(prefix="/reservas", tags=["Reserva"])


@router.get("/", response_model=RespuestaPaginada,
            summary=f"Listar todas las reservas",
            description=f"Lista todas las reservas registradas en el sistema")
def listar_reservas(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description=f"Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description=f"Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    reservas = serv_reserva.leer_todos(db, pagina, tamanio)
    return reservas


@router.get("/{id_reserva}",
            response_model=ReservaResponse,
            summary=f"Obtener el detalle de una reserva",
            description=f"Obtiene los detalles de una reserva registrada en el sistema")
def obtener_reserva(id_reserva: int, db: Session = Depends(leer_bd)):
    reserva = serv_reserva.leer(db, id_reserva)
    return reserva


@router.post("/",
             response_model=ReservaResponse,
             summary="Registrar una Reserva",
             description="Registra una nueva reserva en el sistema")
def crear_reserva(
        reserva: ReservaCreate,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    reserva_creada = serv_reserva.crear(
        db=db,
        obj=reserva.model_dump(),
        usuario_reg=usuario,
        ip_reg=ip)
    return reserva_creada


@router.put("/{id_reserva}",
            response_model=ReservaResponse,
            summary=f"Actualizar una Reserva",
            description=f"Actualiza los datos de una reserva registrada en el sistema")
def actualizar_reserva(
        id_reserva: int,
        reserva: ReservaCreate,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    reserva_actualizada = serv_reserva.actualizar(
        db=db,
        id_obj=id_reserva,
        obj=reserva.model_dump(),
        usuario_mod=usuario,
        ip_mod=ip)
    return reserva_actualizada


@router.delete("/{id_reserva}",
               response_model=bool,
               summary="Eliminar una Reserva",
               description="Elimina una reserva registrada en el sistema")
def eliminar_reserva(
        id_reserva: int,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    reserva_eliminada = serv_reserva.eliminar(
        db=db,
        id_obj=id_reserva,
        usuario_mod=usuario,
        ip_mod=ip)
    return reserva_eliminada


@router.get("/turnos/{id_turno}",
            response_model=RespuestaPaginada,
            summary=f"Listar todas las reservas por turno",
            description=f"Lista todas las reservas registradas en el sistema por turno")
def listar_reservas_por_turno(
    id_turno: int,
    pagina: int = Query(1, alias="pagina", ge=1,
                        description=f"Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description=f"Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    reservas = serv_reserva.leer_reserva_turno(db, id_turno, pagina, tamanio)
    return reservas


@router.get("/pacientes/{id_paciente}",
            response_model=RespuestaPaginada,
            summary=f"Listar todas las reservas por paciente",
            description=f"Lista todas las reservas registradas en el sistema por paciente")
def listar_reservas_por_paciente(
    id_paciente: int,
    pagina: int = Query(1, alias="pagina", ge=1,
                        description=f"Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description=f"Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    reservas = serv_reserva.leer_reserva_paciente(
        db, id_paciente, pagina, tamanio)
    return reservas

@router.put('/estado/{id_reserva}',
            response_model=ReservaResponse,
            summary=f"Actualizar el estado de una reserva",
            description=f"Actualiza el estado de una reserva registrada en el sistema")
def actualizar_estado_reserva(
        id_reserva: int,
        estado: str,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)
        ):
    # Usamos el nuevo método que no filtra por estado_reg='V'
    reserva = serv_reserva.leer_sin_filtro_estado(db, id_reserva)
    
    usuario = token["nombre_usuario"]
    ip = request.client.host
    
    reserva.estado_reg = estado
    reserva.usuario_reg = usuario
    reserva.fecha_reg = datetime.now()
    reserva.ip_mod = ip
    db.commit()
    db.refresh(reserva)
    return reserva
