from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.consulta import ServicioConsulta
from app.componentes.siis1n.esquemas.consulta import ConsultaPaginada, ConsultaCreate, ConsultaResponse
from app.nucleo.baseDatos import leer_bd
from app.nucleo.seguridad import verificar_token
serv_consulta = ServicioConsulta()

router = APIRouter(prefix="/consultas", tags=["Consultas"])

@router.get("/", response_model=ConsultaPaginada,
            summary="listar todas las consultas",
            description="Listra todas las consultas registradas y vigentes en el sistema")
def listar_consultas(
        pagina: int = Query(1, alias="pagina", ge=1,
                            description="Numero de pagina a mostrar"),
        tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                             description="Cantidad de registros a mostrar"),
        db: Session = Depends(leer_bd)):
    consultas = serv_consulta.leer_todos(db, pagina, tamanio)
    return consultas