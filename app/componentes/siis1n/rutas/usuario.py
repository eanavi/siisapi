from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.usuario import ServicioUsuario
from app.componentes.siis1n.esquemas.usuario import RespuestaPaginada, UsuarioCreate, UsuarioResponse
from app.nucleo.seguridad import verificar_token
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
    usuario = serv_usuario.leer(db, id_usuario)
    return usuario


@router.post("/",
             response_model=UsuarioResponse,
             summary="Registrar un Usuario",
             description="Registra un nuevo usuario en el sistema"
             )
def crear_usuario(
        usuario: UsuarioCreate,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario_reg = token["nombre_usuario"]
    ip = request.client.host
    usuario_creado = serv_usuario.crear(
        db=db,
        obj=usuario.model_dump(),
        usuario_reg=usuario_reg,
        ip_reg=ip
    )
    return usuario_creado


@router.delete("/{id_usuario}",
               response_model=UsuarioResponse,
               summary="Eliminar un Usuario",
               description="Elimina un usuario del sistema"
               )
def eliminar_usuario(
        id_usuario: int,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario_reg = token["nombre_usuario"]
    ip = request.client.host
    usuario_eliminado = serv_usuario.eliminar(
        db=db,
        id=id_usuario,
        usuario_reg=usuario_reg,
        ip_reg=ip
    )
    return usuario_eliminado
