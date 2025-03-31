import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from .configuracion import config

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

contexto_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="auth/login")


def verificar_clave(clave_plana, clave_encriptada):
    """ Verifica si una contraseña en texto plano coincide con el hash almacenado """
    return contexto_pwd.verify(clave_plana, clave_encriptada)


def generar_clave_encriptata(clave):
    """ Genera un hash seguro para una contraseña """
    return contexto_pwd.hash(clave)


def crear_token_acceso(data: dict, expira_en: Optional[int] = None):
    datos_codificados = data.copy()
    expiracion = datetime.now(
        timezone.utc) + timedelta(minutes=expira_en or ACCESS_TOKEN_EXPIRE_MINUTES)
    datos_codificados.update({"exp": expiracion})
    return jwt.encode(datos_codificados, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str = Depends(esquema_oauth2)):
    """ Decodifica y verifica la validez del token JWT  """
    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        decodificado = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nombre_usuario: str = decodificado.get("sub")
        rol: str = decodificado.get("rol")
        if nombre_usuario is None or rol is None:
            raise excepcion_credenciales
        return {"nombre_usuario": nombre_usuario, "rol": rol}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise excepcion_credenciales
