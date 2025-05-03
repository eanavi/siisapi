from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.componentes.siis1n.servicios.prestacion import ServicioPrestacion
from app.componentes.siis1n.esquemas.prestacion import PrestacionPaginada, PrestacionCreate, PrestacionResponse
from app.nucleo.baseDatos import leer_bd
from app.nucleo.seguridad import verificar_token

serv_prestacion = ServicioPrestacion()

router = APIRouter(prefix="/prestaciones", tags=["Prestaciones"])


@router.get("/", response_model=PrestacionPaginada,
            summary="listar todas las prestaciones",
            description="Listra todas las prestaciones registradas y vigentes en el sistema")
def listar_prestaciones(
        pagina: int = Query(1, alias="pagina", ge=1,
                            description="Numero de pagina a mostrar"),
        tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                             description="Cantidad de registros a mostrar"),
        db: Session = Depends(leer_bd)):
    prestaciones = serv_prestacion.leer_todos(db, pagina, tamanio)
    return prestaciones


@router.get("/{id_prestacion}", response_model=PrestacionResponse,
            summary=f"Obtener una prestacion por su identificador",
            description=f"Obtiene una prestacion por su ID")
def obtener_prestacion(
        id_prestacion: int,
        db: Session = Depends(leer_bd)):
    """ Obtener una prestacion por su ID """
    prestacion = serv_prestacion.leer(db, id_prestacion)
    return prestacion


@router.post("/", response_model=PrestacionResponse,
             summary="Registrar una nueva Prestacion",
             description="Registra una nueva Prestacion en el Sistema")
def crear_prestacion(
        prestacion: PrestacionCreate,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    """ Crear una nueva prestacion """
    usuario = token["nombre_usuario"]
    ip = request.client.host
    prestacion = serv_prestacion.crear(
        db, prestacion.model_dump(),
        usuario_reg=usuario,
        ip_reg=ip)
    return prestacion


@router.put("/{id_prestacion}",
            response_model=PrestacionResponse,
            summary="Actualizar una prestacion",
            description="Actualiza los datos de una prestacion registrada en el sistema"
            )
def actualizar_prestacion(
        id_prestacion: int,
        prestacion: PrestacionResponse,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    """ Actualizar una prestacion """
    prestacion = serv_prestacion.actualizar(
        db, id_prestacion, prestacion.model_dump())
    return prestacion


@router.delete("/{id_prestacion}",
               response_model=PrestacionResponse,
               summary="Eliminar una prestacion",
               description="Elimina una prestacion registrada en el sistema")
def eliminar_prestacion(
        id_prestacion: int,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    """ Eliminar una prestacion """
    usuario = token["nombre_usuario"]
    ip = request.client.host
    prestacion = serv_prestacion.eliminar(
        db,
        id=id_prestacion,
        usuario_reg=usuario,
        ip_reg=ip)
    return prestacion
