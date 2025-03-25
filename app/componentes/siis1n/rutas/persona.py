from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..servicios.persona import ServicioPersona
from ..esquemas.persona import RespuestaPaginada, PersonaResponse
from app.nucleo.baseDatos import leer_bd
from typing import List


serv_persona  = ServicioPersona()

router = APIRouter(prefix="/personas", tags=["Personas"])

@router.get("/", response_model=RespuestaPaginada, summary="Listar todas las Personas",
            description="Lista todas las personas registradas en el sistema")
def listar_personas(
    pagina: int = Query(1, alias="pagina", ge=1, description="Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50, description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    personas = serv_persona.leer_todos(db, pagina, tamanio)
    return personas


@router.get("/buscar/{criterio}", response_model=RespuestaPaginada, summary="Buscar un conjunto de Personas",
            description="Busca un conjunto de personas registradas en el sistema a partir del criterio de busqueda")
def buscar_personas(
    criterio: str,
    pagina: int = Query(1, alias="pagina", ge=1, description="Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50, description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    personas = serv_persona.buscar_persona(db, criterio, pagina, tamanio)
    return personas

@router.get("/{id_persona}", response_model=PersonaResponse, summary="Obtener una Persona detallada",
            description="Obtiene los detalles de una persona registrada en el sistema")
def obtener_persona(id_persona: UUID, db: Session = Depends(leer_bd)):
    try:
        persona = serv_persona.leer(db, id_persona)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        return persona
    except Exception as e:
        print(f"Error al obtener la persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener la persona: {str(e)}")