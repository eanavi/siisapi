import sys
import os

# Agregamos el directorio raíz del proyecto al sys.path para que se pueda encontrar el módulo 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.nucleo.baseDatos import leer_bd, init_bd
from app.componentes.siis1n.rutas import router as siis1n_router
from app.componentes.soaps.rutas import router as soaps_router
from app.componentes.fhir.rutas import router as fhir_router
from app.middleware.autorizacion import AuthMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text


@asynccontextmanager
async def inicioApp(app: FastAPI):
    try:
        init_bd()
        yield
        print(f"Saliendo de la aplicacion")
    finally:
        print(f"Salida final")

app = FastAPI(
    title="Siis Api",
    description="Api para la gestion del sistema SIIS",
    version="1.1.0",
    contact={
        "name": "Elvis R. Anavi Jiménez",
        "email": "eanavi@gmail.com"
    },
    lifespan=inicioApp
)


origenes = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
]

app.add_middleware(AuthMiddleware)

#modificar para cuando se esta en produccion
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], 
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"]
)

api_router = APIRouter()

api_router.include_router(siis1n_router)
api_router.include_router(soaps_router)
api_router.include_router(fhir_router)

app.include_router(api_router, prefix="/api")


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/api/test-bd")
def test_bd(db: Session = Depends(leer_bd)):
    try:
        db.execute(text('select 1'))
        return {"mensaje": "conexion exitosa"}
    except Exception as e:
        return {"mensaje": f"Error en la bd"}


@app.get("/api/")
def leer_root(request: Request):
    return {"mensaje": "Bienvenido a la Api SiiS"}
