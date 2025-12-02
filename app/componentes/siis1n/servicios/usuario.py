from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import text
from fastapi import HTTPException, status
from .base import ServicioBase
from app.componentes.siis1n.modelos.usuario import Usuario
from app.nucleo.seguridad import verificar_clave, crear_token_acceso, generar_clave_encriptata
from app.nucleo.conexion_cache import guardar_datos_conexion
from app.componentes.siis1n.esquemas.usuario import InformacionUsuario, UsuarioCreate
from sqlalchemy.exc import SQLAlchemyError



class ServicioUsuario(ServicioBase):
    def __init__(self):
        super().__init__(Usuario, 'id_usuario')

    def autenticar(self, db: Session, nombre_usuario: str, clave: str):
        """ Autenticar al usuario verificando credenciales """
        consulta = db.execute(text(f""" select nombre_usuario, clave, nombre_completo, centro_salud, id_centro,
                                     usuario_bd, clave_bd, direccion_bd, puerto, nombre_rol 
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
            "servidor": usuario.direccion_bd,
            "nombre_completo": usuario.nombre_completo,
            "base_datos": "BDEstadistica",
            "usuario": usuario.usuario_bd,
            "clave": usuario.clave_bd,
            "puerto": usuario.puerto,
            "centro_salud": usuario.centro_salud,
            "id_centro": usuario.id_centro,
            "nombre_rol": usuario.nombre_rol
        })

        return token
    
    def crear_usuario(self, db: Session, usuario: UsuarioCreate, usuario_reg: str, ip: str) -> Usuario:
        datos_usuario = {
            "id_empleado": usuario.id_empleado,
            "id_rol": usuario.id_rol,
            "nombre_usuario": usuario.nombre_usuario,
            "clave": generar_clave_encriptata(usuario.clave)
        }
        #Llamamos al metodo crear de la clase base para mantener la logica comun
        nuevo_usuario = self.crear(
            db, datos_usuario, usuario_reg, ip, relaciones=['empleado']
        )
        return nuevo_usuario

    def leer_por_nombre(self, db: Session, nombre_usuario: str):
        consulta = db.execute(text(f""" select nombre_persona, nombre_rol, cargo, 
                                        from fn_nombre_usuario(:criterio)
                                        """), {'criterio': nombre_usuario})
        usuarioFront = consulta.mappings().first()
        if not usuarioFront:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuarioFront

    def obtener_informacion_usuario(self, db: Session, usuario:str) -> InformacionUsuario:
        try:
            resultado = db.execute(
                text("""SELECT * FROM public.fn_obtener_perfil_usuario(:nombre_usuario)"""),
                {'nombre_usuario': usuario}
            )
            fila = resultado.mappings().first()
            if not fila:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Información para el usuario '{usuario}' no encontrada."
                )
            return InformacionUsuario(**fila)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al leer la información del usuario: {str(e)}"
            )