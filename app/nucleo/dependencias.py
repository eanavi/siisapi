from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Generator
from app.nucleo.conexion_cache import obtener_datos_conexion
from app.nucleo.bdSoaps import obtener_sesion_mssql
import os
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

LLAVE_SECRETA = os.getenv("SECRET_KEY", "pr0gr4m4t1c4")
ALGORITMO = os.getenv("ALGORITHM", "HS256")


def obtener_bd_mssql(token: str = Depends(oauth2_scheme)) -> Generator[Session, None, None]:
    try:
        payload = jwt.decode(token, LLAVE_SECRETA, algorithms=[ALGORITMO])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"Authorization": "Bearer"}
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"Authorization": "Bearer"}
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al decodificar el token",
            headers={"Authorization": "Bearer"}
        )
    datos_conexion = obtener_datos_conexion(token)
    if not datos_conexion:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Datos de conexión no encontrados",
            headers={"Authorization": "Bearer"}
        )

    try:
        sesion = next(obtener_sesion_mssql(
            servidor=datos_conexion["servidor"],
            base_datos=datos_conexion["base_datos"],
            usuario=datos_conexion["usuario"],
            clave=datos_conexion["clave"],
            puerto=datos_conexion["puerto"]
        ))
        return sesion
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la sesión de la base de datos",
            headers={"Authorization": "Bearer"}
        )
