from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
import re
import os
from app.nucleo.seguridad import SECRET_KEY, ALGORITHM


PERMISOS_ROLES = {
    "GET": {
        "/personas": ["Administrador", "operador", "Medico"],
        "/usuarios": ["Administrador", "operador"],
        "/consultas": ["Administrador", "operador", "Medico"],
        "/empleados": ["Administrador"],
        "/grupos": ["Administrador"],
        "/listas": ["Administrador"],
        "/soaps": ["Administrador"],
        "/pacientes": ["Administrador", "operador", "Medico"],
        "/prestaciones": ["Administrador", "operador", "Medico"],
        "/menus": ["Administrador", "operador", "Medico"],

    },
    "POST": {
        "/usuarios": ["Administrador"],
        "/consultas": ["medico"],
        "/personas": ["Administrador"],  # Solo médicos pueden crear consultas
        "/grupos": ["Administrador"],
        "/empleados": ["Administrador"],
        "/listas": ["Administrador"],
        "/pacientes": ["Administrador"],
        "/prestaciones": ["Administrador", "operador", "Medico"],
    },
    "PUT": {
        "/usuarios": ["Administrador", "operador"],
        # Solo operador y admin pueden modificar personas
        "/personas": ["administrador", "operador"],
        "/consultas": ["medico"],  # Solo médicos pueden modificar consultas
        "/grupos": ["Administrador"],
        "/empleados": ["Administrador"],
        "/listas": ["Administrador"],
        "/pacientes": ["Administrador", "operador", "Medico"],
        "/prestaciones": ["Administrador", "operador", "Medico"],
    },
    "DELETE": {
        "/usuarios": ["Administrador"],
        # Solo administradores pueden eliminar consultas
        "/consultas": ["Administrador"],
        "/empleados": ["Administrador"],
        "/grupos": ["Administrador"],
        "/listas": ["Administraor"],
        "/pacientes": ["Administrador"],
    }
}


def normalizar_ruta(ruta: str) -> str:
    ruta_normalizada = re.match(r"(/[\w-]+)", ruta).group(1)
    return ruta_normalizada


class AuthMiddleware(BaseHTTPMiddleware):
    """ Middleware para autenticacion y autorizacion granular de rutas """

    async def dispatch(self, request, call_next):

        # if os.getenv("TEST_ENV") == "true":
        #    return await call_next(request)
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Elegimos solo la ruta
        ruta = normalizar_ruta(request.url.path)
        metodo = request.method

        if request.url.path.startswith("/auth/login"):
            return await call_next(request)

        if metodo not in PERMISOS_ROLES or ruta not in PERMISOS_ROLES[metodo]:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": f"Acceso denegado a {ruta} ({metodo})."}
            )

        token = request.headers.get("authorization")
        if not token or not token.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Autenticacion requerida"}
            )
        try:
            token = token.split(" ")[1]
            decodificado = jwt.decode(
                token, SECRET_KEY, algorithms=[ALGORITHM])
            usuario = decodificado.get("sub")
            rol = decodificado.get("rol")

            if not usuario or not rol:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalido"
                )

            if rol not in PERMISOS_ROLES[metodo][ruta]:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": f"No tienes permisos para acceder a {ruta}({metodo})."}
                )
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token expirado"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token inválido"}
            )

        try:
            return await call_next(request)
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Error interno del servidor"}
            )
