from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
import re
import os
from app.nucleo.seguridad import SECRET_KEY, ALGORITHM


PERMISOS_ROLES = {
    "GET": {
        "/personas": ["Administrador", "Operador"],
        "/usuarios": ["Administrador", "Operador", "Medico", "Enfermera"],
        "/consultas": ["Administrador", "Operador", "Medico", "Enfermera"],
        "/empleados": ["Administrador", "Operador"],
        "/grupos": ["Administrador", "Operador"],
        "/listas": ["Administrador", "Operador"],
        "/soaps": ["Administrador"],
        "/fhir":["Administrador"],
        "/pacientes": ["Administrador", "Operador", "Medico", "Enfermera"],
        "/prestaciones": ["Administrador", "Operador", "Medico"],
        "/menus": ["Administrador", "Operador", "Medico", "Enfermera"],
        "/turnos": ["Administrador", "Operador", "Medico", "Enfermera"],
        "/reservas": ["Administrador", "Operador", "Medico", "Enfermera"],

    },
    "POST": {
        "/usuarios": ["Administrador", "Operador"],
        "/consultas": ["Administrador","Medico", "Enfermera"],
        "/personas": ["Administrador"],  # Solo médicos pueden crear consultas
        "/grupos": ["Administrador", "Operador"],
        "/empleados": ["Administrador", "Operador"],
        "/listas": ["Administrador", "Operador"],
        "/pacientes": ["Administrador", "Operador", "Medico", "Enfermera"],
        "/prestaciones": ["Administrador", "Operador", "Medico"],
        "/turnos": ["Administrador", "Operador", "Medico", "Enfermera"],
    },
    "PUT": {
        "/usuarios": ["Administrador", "Operador", "Medico", "Enfermera"],
        # Solo Operador y admin pueden modificar personas
        "/personas": ["administrador", "Operador"],
        "/consultas": ["Medico", "Enfermera"],  # Solo médicos pueden modificar consultas
        "/grupos": ["Administrador"],
        "/empleados": ["Administrador"],
        "/listas": ["Administrador", "Operador"],
        "/pacientes": ["Administrador", "Operador", "Medico", "Enfermera"],
        "/prestaciones": ["Administrador", "Operador", "Medico", "Enfermera"],
        "/menus": ["Administrador", "Operador", "Medico", "Enfermera"],
        "/reservas": ["Administrador", "Operador", "Medico", "Enfermera"],

    },
    "DELETE": {
        "/usuarios": ["Administrador"],
        # Solo administradores pueden eliminar consultas
        "/consultas": ["Administrador"],
        "/empleados": ["Administrador"],
        "/grupos": ["Administrador"],
        "/listas": ["Administraor"],
        "/pacientes": ["Administrador"],
        "/turnos": ["Administrador"],
    }
}


def normalizar_ruta(ruta: str) -> str:
    # 1. Quitamos el prefijo /api si existe al inicio
    ruta_sin_api = re.sub(r"^/api", "", ruta)
    
    # 2. Si quedó vacía o es solo '/', retornamos '/'
    if not ruta_sin_api or ruta_sin_api == "/":
        return "/"
    
    # 3. Tu lógica original para capturar el primer segmento (/personas, /usuarios, etc.)
    match = re.match(r"(/[\w-]+)", ruta_sin_api)
    return match.group(1) if match else ruta_sin_api




class AuthMiddleware(BaseHTTPMiddleware):
    """ Middleware para autenticacion y autorizacion granular de rutas """

    async def dispatch(self, request, call_next):

        # if os.getenv("TEST_ENV") == "true":
        #    return await call_next(request)
        if request.url.path in ["/api/","/favicon.ico","/api/test-bd","/api/docs", "/api/redoc", "/api/openapi.json"]:
            return await call_next(request)

        

        # Elegimos solo la ruta
        ruta = normalizar_ruta(request.url.path)
        metodo = request.method

        if request.url.path.startswith("/api/auth/login"):
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
                        "detail": f"No tienes permisos para acceder a {ruta}({metodo}){rol} ."}
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
