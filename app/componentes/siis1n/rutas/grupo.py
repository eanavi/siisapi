from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.grupo import ServicioGrupo
from app.componentes.siis1n.esquemas.grupo import GrupoPaginado, ListaGrupo, GrupoCreate, GrupoResponse
from app.nucleo.baseDatos import leer_bd
from app.nucleo.seguridad import verificar_token


serv_grupo = ServicioGrupo()

router = APIRouter(prefix="/grupos", tags=["Grupos"])


@router.get(
    "/",
    response_model=GrupoPaginado,
    summary="Listar todos los grupos",
    description="Lista todos los grlupos registrados y vigentes en el sistema"
)
def listar_grupos(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description="Numero de pagia a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    grupos = serv_grupo.leer_todos(db, pagina, tamanio)
    return grupos


@router.get("/{id_grupo}",
            response_model=GrupoResponse,
            summary=f"Obtener un grupo por su identificador",
            description=f"Obtiene todos los datos de un grupo por su ID"
            )
def obtener_grupo(id_grupo: int, db: Session = Depends(leer_bd)):
    grupo = serv_grupo.leer(db, id_grupo)
    return grupo


@router.post("/",
             response_model=GrupoResponse,
             summary=f"Registrar un grupo  de listas",
             description=f"Registra un nuevo grupo de liastas en el sistema"
             )
def crear_grupo(
    grupo: GrupoCreate,
    db: Session = Depends(leer_bd),
):
    grupo_creado = serv_grupo.crear(
        db=db,
        obj=grupo.model_dump()
    )
    return grupo_creado


@router.put("/{id_grupo}",
            response_model=GrupoResponse,
            summary=f"Actualiza un Grupo",
            description=f"Actualiza los datos de un grupo de Listas en el sistema"
            )
def actualizar_grupo(
        id_grupo: int,
        grupo: GrupoCreate,
        db: Session = Depends(leer_bd)):
    grupo_actualizado = serv_grupo.actualizar(db, id_grupo, grupo.model_dump())
    return grupo_actualizado


@router.delete("/{id_grupo}",
               response_model=bool,
               summary=f"Eliminar un grupo",
               description=f"Elimina un grupo registrado en el sistema"
               )
def eliminar_grupo(
        id_grupo: int,
        db: Session = Depends(leer_bd)):
    resultado = serv_grupo.eliminar(
        db=db,
        id=id_grupo
    )
    return resultado
