from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.menu import ServicioMenu
from app.componentes.siis1n.esquemas.menu import MenuPaginado, MenuResponse, MenuCreate, MenuRol
from app.componentes.siis1n.esquemas.usuario import InformacionUsuario
from typing import List
from app.nucleo.baseDatos import leer_bd

serv_menu = ServicioMenu()
router = APIRouter(prefix="/menus", tags=["Menus"])
@router.get("/", response_model=MenuPaginado,
            summary="Listar todos los menus",
            description="Lista todos los menus registrados en el sistema")
def listar_menus(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description="Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    menus = serv_menu.leer_todos(db, pagina, tamanio)
    return menus

@router.get("/{id_menu}", response_model=MenuResponse,
            summary="Obtener menu por ID",
            description="Obtiene un menu por su ID")
def obtener_menu(id_menu: int, db: Session = Depends(leer_bd)):
    menu = serv_menu.leer(db, id_menu)
    return menu

@router.get("/rol/{nombre_rol}", response_model=List[MenuRol],
            summary="Obtener menus por rol",
            description="Obtiene los menus asociados a un rol")
def obtener_menus_por_rol(nombre_rol: str, db: Session = Depends(leer_bd)):
    menus = serv_menu.obtener_menus_por_rol(db, nombre_rol)
    return menus

@router.get("/rol/{nombre_usuario}", response_model=List[MenuRol],
            summary="Obtener menus por usuario",
            description="Obtiene los menus asociados a un usuario")
def obtener_menus_por_usuario(nombre_usuario: str, db: Session = Depends(leer_bd)):
    menus = serv_menu.obtener_menus_por_usuario(db, nombre_usuario)
    return menus

