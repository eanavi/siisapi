from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.componentes.siis1n.servicios.rol import ServicioRol
from app.componentes.siis1n.esquemas.rol import RolResponse, RespuestaPaginada, RolCreate
from app.nucleo.baseDatos import leer_bd

serv_rol = ServicioRol()

router = APIRouter(prefix="/rol", tags=["Rol"])


@router.get("/", response_model=RespuestaPaginada,
            summary=f"Listar todos los roles",
            description=f"Lista todos los roles registrados en el sistema")
def listar_roles(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description=f"Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description=f"Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    roles = serv_rol.leer_todos(db, pagina, tamanio)
    return roles


@router.get("/{id_rol}",
            response_model=RolResponse,
            summary=f"Obtener el detalle de un rol",
            description=f"Obtiene los detalles de un rol registrado en el sistema")
def obtener_rol(id_rol: int, db: Session = Depends(leer_bd)):
    try:
        rol = serv_rol.leer(db, id_rol)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con id {id_rol} no encontrado"
            )
        return rol
    except Exception as e:
        print(f"Error al obtener el rol: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el rol: {str(e)}"
        )


@router.post("/",
             response_model=RolResponse,
             summary="Registrar un Rol",
             description="Registra un nuevo rol en el sistema"
             )
def crear_rol(rol: RolCreate, db: Session = Depends(leer_bd)):
    try:
        rol_creado = serv_rol.crear(db, rol.model_dump())
        return rol_creado
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el rol en la bd: {str(e)}"
        )
    except HTTPException as htp_es:
        raise htp_es
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al crear el rol: {str(e)}"
        )


@router.put("/{id_rol}",
            response_model=RolResponse,
            summary=f"Actualizar un Rol",
            description=f"Actualiza los datos de un rol registrado en el sistema")
def actualizar_rol(id_rol: int, rol: RolCreate, bd: Session = Depends(leer_bd)):
    try:
        rol_actualizado = serv_rol.actualizar(
            bd, id_rol, rol.model_dump())
        return rol_actualizado
    except SQLAlchemyError as e:
        bd.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el Rol en la bd: {str(e)}"
        )
    except HTTPException as htpex:
        raise htpex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al atualizar el rol: {str(e)}"
        )


@router.delete("/{id_rol}",
               response_model=bool,
               summary="Eliminar un Rol",
               description="Elimina un rol registrado en el sistema")
def eliminar_rol(id_rol: int, db: Session = Depends(leer_bd)):
    if not serv_rol.eliminar(db, id_rol):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rol no encontrado"
        )
