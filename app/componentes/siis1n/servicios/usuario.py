from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .base import ServicioBase
from app.componentes.siis1n.modelos.usuario import Usuario
from app.nucleo.seguridad import verificar_clave, crear_token_acceso


class ServicioUsuario(ServicioBase):
    def __init__(self):
        super().__init__(Usuario, 'id_usuario')

    def autenticar(self, db: Session, nombre_usuario: str, clave: str):
        """ Autenticar al usuario verificando credenciales """
        usuario = db.query(Usuario).filter(
            Usuario.nombre_usuario == nombre_usuario).first()
        if not usuario or not verificar_clave(clave, usuario.clave):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o clave incorrectos"
            )
        return crear_token_acceso({"sub": usuario.nombre_usuario, "rol": usuario.rol.nombre})
