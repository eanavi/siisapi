from fastapi import FastAPI, Request, Depends
from app.nucleo.baseDatos import leer_bd, init_bd
from app.componentes.siis1n.rutas import router as siis1n_router
from app.componentes.soaps.rutas import router as soaps_router
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

app.add_middleware(AuthMiddleware)

app.include_router(siis1n_router)
app.include_router(soaps_router)


@app.get("/test-bd")
def test_bd(db: Session = Depends(leer_bd)):
    try:
        db.execute(text('select 1'))
        return {"mensaje": "conexion exitosa"}
    except Exception as e:
        return {"mensaje": f"Error en la bd"}


@app.get("/")
def leer_root(request: Request):
    return {"mensaje": "Bienvenido a la Api SiiS"}
