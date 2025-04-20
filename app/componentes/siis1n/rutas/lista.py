from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.lista import ServicioLista
from app.componentes.siis1n.esquemas.lista import RespuestaPaginada, ListaResponse, ListaCreate, ListaRespuesta
from typing import List
from app.nucleo.baseDatos import leer_bd

serv_lista = ServicioLista()

router = APIRouter(prefix="/listas", tags=["Listas"])


@router.get("/", response_model=RespuestaPaginada,
            summary=f"Listar todas las listas",
            description=f"Lista todas las listas registradas en el sistema")
def listar_listas(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description=f"Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description=f"Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    listas = serv_lista.leer_todos(db, pagina, tamanio)
    return listas


@router.get("/{id_lista}", response_model=ListaResponse,
            summary=f"Obtener lista por ID",
            description=f"Obtiene una lista por su ID")
def obtener_lista(id_lista: int, db: Session = Depends(leer_bd)):
    lista = serv_lista.leer(db, id_lista)
    return lista


@router.get("/grupo/{grupo}", response_model=List[ListaRespuesta],
            summary=f"Obtener lista por grupo",
            description=f"Obtiene una lista por su grupo")
def obtener_lista_grupo(grupo: str, db: Session = Depends(leer_bd)):
    lista = serv_lista.obtener_lista_por_grupo(db, grupo)
    return lista


@router.post("/",
             response_model=ListaResponse,
             summary="Registrar una nueva lista",
             description="Registra una nueva lista en el sistema"
             )
def crear_lista(
        lista: ListaCreate,
        db: Session = Depends(leer_bd)):
    lista_creada = serv_lista.crear(db=db, obj=lista.model_dump())
    return lista_creada


@router.put("/{id_lista}",
            response_model=ListaResponse,
            summary=f"Actualiza un item de una lista",
            description=f"Actualiza los datos de un item de una lista en el sistema")
def actualizar_lista(id_lista: int, lista: ListaCreate, bd: Session = Depends(leer_bd)):
    lista_actualizada = serv_lista.actualizar(bd, id_lista, lista.model_dump())
    return lista_actualizada


@router.delete("/{id_lista}",
               response_model=bool,
               summary="Eliminar un item de una lista",
               description=f"Elimina un item de una lista en el sistema")
def eliminar_lista(
        id_lista: int,
        db: Session = Depends(leer_bd)):
    resultado = serv_lista.eliminar(
        db=db,
        id=id_lista)
    return resultado
