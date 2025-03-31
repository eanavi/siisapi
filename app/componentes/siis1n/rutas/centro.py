from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.componentes.siis1n.servicios.centro import ServicioCentro
from app.componentes.siis1n.esquemas.centro import CentroPaginado, CentroCreate, CentroResponse
from app.nucleo.baseDatos import leer_bd

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
    try:
        centro = serv_centro.leer(db, id_centro)
        if not centro:
            raise HTTPException(
                status_code=404, detail="Centro de Salud no encontrado"
            )
        return centro
    except Exception as e:
        print(f"Error al obtener el centro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el centro de salud: {str(e)}"
        )


@router.post("/", response_model=CentroResponse,
             summary="Registrar un nuevo Centro de Salud",
             description="Registra un nuevo Centro de Salud en el Sistema")
def crear_centro_salud(centro_salud: CentroCreate, db: Session = Depends(leer_bd)):
    try:
        centro = serv_centro.crear(db, centro_salud)
        return centro
    except SQLAlchemyError as e:
        print(f"Error al crear el centro de salud: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el empleado: {str(e)}"
        )
    except HTTPException as ht_ex:
        raise ht_ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al crear el centro de salud: {str(e)}"
        )


@router.put("/{id_centro}",
            response_model=CentroResponse,
            summary="Actualizar un centro de salud",
            description="Actualiza los datos de un centro de salud registrado en el sistema"
            )
def actualizar_centro(id_centro: int, centro: CentroCreate, db: Session = Depends(leer_bd)):
    try:
        centro_actualizado = serv_centro.actualizar(
            db, id_centro, centro.model_dump()
        )
        return centro_actualizado
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el centro de salud en la base de datos: {str(e)}"
        )
    except HTTPException as ht_ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al actualizar la persona: {str(e)}"
        )


@router.delete("/{id_centro}",
               response_model=bool,
               summary=f"Eliminar un Centro de Salud",
               description=f"Elimina un centro de salud registrado en el sistema"
               )
def eliminar_centro(id_centro: int, db: Session = Depends(leer_bd)):
    if not serv_centro.eliminar(db, id_centro):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Centro de Salud no encontrado"
        )
    return True
