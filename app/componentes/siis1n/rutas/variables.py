from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.variables import ServicioVariables
from app.componentes.siis1n.esquemas.variables import VariableResponse, RespuestaPaginada, VariableCreate
from app.nucleo.seguridad import verificar_token
from app.nucleo.baseDatos import leer_bd

serv_var = ServicioVariables()

router = APIRouter(prefix="/variables", tags=["Variables"])


@router.get("/", response_model=RespuestaPaginada,
            summary=f"Listar todas las variables",
            description=f"Lista todas las variables registradas en el sistema")
def listar_variables(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description=f"Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description=f"Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    variables = serv_var.leer_todos(db, pagina, tamanio)
    return variables


@router.get("/{id_variable}",
            response_model=VariableResponse,
            summary=f"Obtener el detalle de una variable",
            description=f"Obtiene los detalles de una variable registrada en el sistema")
def obtener_variable(id_variable: int, db: Session = Depends(leer_bd)):
    variable = serv_var.leer(db, id_variable)
    return variable


@router.post("/",
             response_model=VariableResponse,
             summary="Registrar una Variable",
             description="Registra una nueva variable en el sistema"
             )
def crear_variable(
        variable: VariableCreate,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    variable_creada = serv_var.crear(
        db=db,
        obj=variable.model_dump(),
        usuario_reg=usuario,
        ip_reg=ip)
    return variable_creada


@router.put("/{id_variable}",
            response_model=VariableResponse,
            summary=f"Actualizar una Variable",
            description=f"Actualiza los datos de una variable registrada en el sistema")
def actualizar_variable(
        id_variable: int,
        variable: VariableCreate,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    variable_actualizada = serv_var.actualizar(
        db=db,
        id_obj=id_variable,
        obj=variable.model_dump(),
        usuario_mod=usuario,
        ip_mod=ip)
    return variable_actualizada


@router.delete("/{id_variable}",
               response_model=bool,
               summary="Eliminar una Variable",
               description="Elimina una variable registrada en el sistema")
def eliminar_variable(
        id_variable: int,
        request: Request,
        db: Session = Depends(leer_bd),
        token: str = Depends(verificar_token)):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    variable_eliminada = serv_var.eliminar(
        db=db,
        id_obj=id_variable,
        usuario_mod=usuario,
        ip_mod=ip)
    return variable_eliminada
