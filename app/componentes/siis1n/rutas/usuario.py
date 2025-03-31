from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.componentes.siis1n.servicios.usuario import ServicioUsuario
from app.componentes.siis1n.esquemas.usuario import RespuestaPaginada, UsuarioCreate, UsuarioResponse
from app.nucleo.baseDatos import leer_bd

serv_usuario = ServicioUsuario()
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=RespuestaPaginada,
            summary=f"Listar todos los Usuarios",
            description=f"Lista todos los usuarios registrados en el sistema")
def listar_usuarios(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description=f"Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description=f"Cant5idad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    usuarios = serv_usuario.leer_todos(db, pagina, tamanio)
    return usuarios


@router.get("/{id_usuario}", response_model=UsuarioResponse,
            summary=f"Obtener Usuario por ID",
            description=f"Obtiene un usuario por su II")
def obtner_usuario(id_usuario: int, db: Session = Depends(leer_bd)):
    try:
        usuario = serv_usuario.leer(db, id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario
    except Exception as e:
        print(f"Error al obtrener el usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el usuario: {str(e)}"
        )
