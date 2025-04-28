from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from fastapi import HTTPException, status
from .base import ServicioBase
from app.componentes.siis1n.modelos.usuario import Usuario
from app.nucleo.seguridad import verificar_clave, crear_token_acceso
from app.nucleo.conexion_cache import guardar_datos_conexion


class ServicioUsuario(ServicioBase):
    def __init__(self):
        super().__init__(Usuario, 'id_usuario')

    def autenticar(self, db: Session, nombre_usuario: str, clave: str):
        """ Autenticar al usuario verificando credenciales """
        consulta = db.execute(text(f""" select nombre_usuario, clave, centro_salud, id_centro,
                                     usuario, clave_centro, direccion, puerto, nombre_rol 
                                     from fn_usuario(:criterio)
                                     """), {'criterio': nombre_usuario})
        usuario = consulta.mappings().first()
        if not usuario or not verificar_clave(clave, usuario.clave):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o clave incorrectos"
            )
        token = crear_token_acceso(
            {"sub": usuario.nombre_usuario, "rol": usuario.nombre_rol})
        guardar_datos_conexion(token, {
            "servidor": usuario.direccion,
            "base_datos": "BDEstadistica",
            "usuario": usuario.usuario,
            "clave": usuario.clave_centro,
            "puerto": usuario.puerto,
            "centro_salud": usuario.centro_salud,
            "id_centro": usuario.id_centro,
            "nombre_rol": usuario.nombre_rol
        })

        return token
