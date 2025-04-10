from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.persona import ServicioPersona
from app.componentes.siis1n.esquemas.persona import RespuestaPaginada, PersonaResponse, PersonaCreate
from app.nucleo.seguridad import verificar_token
from app.nucleo.baseDatos import leer_bd


serv_persona = ServicioPersona()

router = APIRouter(prefix="/personas", tags=["Personas"])


@router.get("/",
            response_model=RespuestaPaginada,
            dependencies=[Depends(verificar_token)],
            summary="Listar todas las Personas",
            description="Lista todas las personas registradas en el sistema")
def listar_personas(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description="Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    personas = serv_persona.leer_todos(db, pagina, tamanio)
    return personas


@router.get("/buscar/{criterio}",
            response_model=RespuestaPaginada,
            summary="Buscar un conjunto de Personas",
            description="Busca un conjunto de personas registradas en el \
                sistema a partir del criterio de busqueda"
            )
def buscar_personas(
    criterio: str,
    pagina: int = Query(1, alias="pagina", ge=1,
                        description="Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    personas = serv_persona.buscar_persona(db, criterio, pagina, tamanio)
    return personas


@router.get("/{id_persona}",
            response_model=PersonaResponse,
            summary="Obtener una Persona detallada",
            description="Obtiene los detalles de una persona registrada en el sistema")
def obtener_persona(id_persona: UUID, db: Session = Depends(leer_bd)):
    persona = serv_persona.leer(db, id_persona)
    return persona


@router.post("/",
             response_model=PersonaResponse,
             summary="Registrar una Persona",
             description="Registra una nueva persona en el sistema"
             )
def crear_persona(persona: PersonaCreate, db: Session = Depends(leer_bd)):
    persona_creada = serv_persona.crear(db, persona.model_dump())
    return persona_creada


@router.put("/{id_persona}",
            response_model=PersonaResponse,
            summary="Actualizar una Persona",
            description="Actualiza los datos de una persona registrada en el sistema")
def actualizar_persona(id_persona: UUID, persona: PersonaCreate,
                       db: Session = Depends(leer_bd)):
    persona_actualizada = serv_persona.actualizar(
        db, id_persona, persona.model_dump())
    return persona_actualizada


@router.delete("/{id_persona}",
               response_model=bool,
               summary="Eliminar una Persona",
               description="Elimina una persona registrada en el sistema")
def eliminar_persona(id_persona: UUID, db: Session = Depends(leer_bd)):
    resultado = serv_persona.eliminar(db, id_persona)
    return resultado


@router.delete("/fisico/{id_persona}",
               response_model=bool,
               summary="Eliminar fisicamente una Persona",
               description="Elimina fisicamente una persona registrada en el sistema"
               )
def eliminar_persona_fisico(id_persona: UUID, db: Session = Depends(leer_bd)):
    resultado = serv_persona.eliminar_fisico(db, id_persona)
    return resultado
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         detail=f"Error al eliminar el objeto: {str(e)}")
