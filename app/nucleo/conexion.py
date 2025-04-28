from fastapi import Depends, Header, HTTPException, status
import os
from . import conexion_cache
from .bdSoaps import obtener_sesion_mssql


def obtener_token(authorization: str = Header(...)) -> str:
    try:
        esquema, token = authorization.split()
        if esquema.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autorización no válido",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al procesar el token",
            headers={"WWW-Authenticate": "Bearer"}
        ) from e


def obtener_datos_conexion(token: str = Depends(obtener_token)) -> dict:
    datos = conexion_cache.obtener_datos_conexion(token)
    if not datos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Datos de conexión no encontrados",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return datos


def obtener_id_centro(datos: dict = Depends(obtener_datos_conexion)) -> int:
    return datos["id_centro"]


def obtener_nombre_centro(datos: dict = Depends(obtener_datos_conexion)) -> str:
    return datos["nombre_centro"]


def obtener_rol_usuario(datos: dict = Depends(obtener_datos_conexion)) -> str:
    return datos["rol_usuario"]


def bd_mssql(datos: dict = Depends(obtener_datos_conexion)):
    try:
        sesion = next(obtener_sesion_mssql(
            servidor=datos["servidor"],
            base_datos="BDEstadistica",
            usuario=datos["usuario"],
            clave=datos["clave"],
            puerto=datos["puerto"]
        ))
        return sesion
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la sesión de la base de datos",
            headers={"WWW-Authenticate": "Bearer"}
        )
