from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.componentes.siis1n.servicios.centro import ServicioCentro
from app.componentes.siis1n.esquemas.centro import CentroPaginado, CentroCreate, CentroResponse
from app.nucleo.baseDatos import leer_bd
from app.nucleo.seguridad import verificar_token


serv_centro = ServicioCentro()

router = APIRouter(prefix="/centros", tags=["Centros"])


@router.get("/", response_model=CentroPaginado,
            summary="listar todos los centros de salud",
            description="Listra todos los centros de salud registrados y \
                vigentes en el sistema")
def listar_centros(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description="Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    centros = serv_centro.leer_todos(db, pagina, tamanio)
    return centros


@router.get("/{id_centro}", response_model=CentroResponse,
            summary=f"Obtener un centro de salud por su identificador",
            description=f"Obtiene un centro de salud por su ID")
def obtener_centro(id_centro: int, db: Session = Depends(leer_bd)):
    centro = serv_centro.leer(db, id_centro)
    return centro


@router.post("/", response_model=CentroResponse,
             summary="Registrar un nuevo Centro de Salud",
             description="Registra un nuevo Centro de Salud en el Sistema")
def crear_centro_salud(
        centro_salud: CentroCreate,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    centro = serv_centro.crear(
        db, centro_salud.model_dump(),
        usuario_reg=usuario,
        ip_reg=ip)
    return centro


@router.put("/{id_centro}",
            response_model=CentroResponse,
            summary="Actualizar un centro de salud",
            description="Actualiza los datos de un centro de salud registrado en el sistema"
            )
def actualizar_centro(id_centro: int, centro: CentroCreate, db: Session = Depends(leer_bd)):
    centro_actualizado = serv_centro.actualizar(
        db, id_centro, centro.model_dump()
    )
    return centro_actualizado


@router.delete("/{id_centro}",
               response_model=bool,
               summary=f"Eliminar un Centro de Salud",
               description=f"Elimina un centro de salud registrado en el sistema"
               )
def eliminar_centro(
        id_centro: int,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    resultado = serv_centro.eliminar(
        db,
        id=id_centro,
        usuario_reg=usuario,
        ip_reg=ip)
    return resultado
