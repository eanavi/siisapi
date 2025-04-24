from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.componentes.soaps.servicios.se_hc import ServicioSe_Hc
from app.componentes.soaps.esquemas.se_hc import Se_Hc, RespuestaPaginada
from app.nucleo.dependencias import obtener_bd_mssql

serv_se_hc = ServicioSe_Hc()

router = APIRouter(prefix="/se_hc", tags=["Se_hc"])


@router.get("/",
            response_model=RespuestaPaginada,
            summary="Listar todas las Personas",
            description="Lista todas las personas registradas en SOAPS"
            )
def listar_pacientes(
        pagina: int = Query(1, alias="pagina", ge=1,
                            description=f"Numero de paginas a mostrar"),
        tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                             description=f"Centidad de registros a mostrar"),
        db: Session = Depends(obtener_bd_mssql)):

    try:
        pacientes = serv_se_hc.leer_todos(db, pagina, tamanio)
        return pacientes
    finally:
        db.close()
