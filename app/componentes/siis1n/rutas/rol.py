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
    rol = serv_rol.leer(db, id_rol)
    return rol


@router.post("/",
             response_model=RolResponse,
             summary="Registrar un Rol",
             description="Registra un nuevo rol en el sistema"
             )
def crear_rol(rol: RolCreate, db: Session = Depends(leer_bd)):
    rol_creado = serv_rol.crear(db, rol.model_dump())
    return rol_creado


@router.put("/{id_rol}",
            response_model=RolResponse,
            summary=f"Actualizar un Rol",
            description=f"Actualiza los datos de un rol registrado en el sistema")
def actualizar_rol(id_rol: int, rol: RolCreate, bd: Session = Depends(leer_bd)):
    rol_actualizado = serv_rol.actualizar(bd, id_rol, rol.model_dump())
    return rol_actualizado


@router.delete("/{id_rol}",
               response_model=bool,
               summary="Eliminar un Rol",
               description="Elimina un rol registrado en el sistema")
def eliminar_rol(id_rol: int, db: Session = Depends(leer_bd)):
    resultado = serv_rol.eliminar(db, id_rol)
    return resultado
