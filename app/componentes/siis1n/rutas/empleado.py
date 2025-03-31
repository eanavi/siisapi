from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.componentes.siis1n.servicios.empleado import ServicioEmpleado
from app.componentes.siis1n.esquemas.empleado import RespuestaPaginada, EmpleadoPersona, EmpleadoResponse
from app.nucleo.baseDatos import leer_bd

serv_empleado = ServicioEmpleado()

router = APIRouter(prefix="/empleados", tags=["Empleados"])


@router.get("/", response_model=RespuestaPaginada, summary="Listar todas los Empleados",
            description="Lista todas los empleados registrados en el sistema")
def listar_personas(
    pagina: int = Query(1, alias="pagina", ge=1,
                        description="Numero de pagina a mostrar"),
    tamanio: int = Query(10, alias="tamanio", ge=1, le=50,
                         description="Cantidad de registros a mostrar"),
    db: Session = Depends(leer_bd)
):
    empleados = serv_empleado.leer_todos(db, pagina, tamanio)
    return empleados


@router.get("/{id_empleado}", response_model=EmpleadoPersona,
            summary="Obtener Empleado por ID",
            description="Obtiene un empleado por su ID")
def obtener_empleado(id_empleado: int, db: Session = Depends(leer_bd)):
    try:
        empleado = serv_empleado.leer_empleado_con_persona(db, id_empleado)
        if not empleado:
            raise HTTPException(
                status_code=404, detail="Empleado no encontrado")

        return empleado
    except Exception as e:
        print(f"Error al obtener el empleado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el empleado: {str(e)}"
        )


@router.post("/", response_model=EmpleadoResponse,
             summary="Registrar un nuevo Empleado",
             description="Registra un nuevo empleado en el sistema")
def crear_empleado(empleado_persona: EmpleadoPersona, db: Session = Depends(leer_bd)):
    try:
        empleado = serv_empleado.crear_empleado_con_persona(
            db, empleado_persona)
        return empleado
    except SQLAlchemyError as e:
        print(f"Error al crear el empleado: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el empleado: {str(e)}"
        )
    except HTTPException as htp_ex:
        raise htp_ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al crear el empleado: {str(e)}"
        )


@router.put("/{id_empleado}", response_model=EmpleadoPersona,
            summary="Actualizar Empleado",
            description="Actualiza un empleado por su ID")
def actualizar_empleado(id_empleado: int, empleado_persona: EmpleadoPersona,
                        db: Session = Depends(leer_bd)):
    try:
        empleado = serv_empleado.actualizar_empleado_con_persona(
            db, id_empleado, empleado_persona)
        if not empleado:
            raise HTTPException(
                status_code=404, detail="Empleado no encontrado")
        return empleado
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error al actualizar el empleado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el empleado: {str(e)}"
        )
    except HTTPException as ht_ex:
        raise ht_ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al actualizar el empleado: {str(e)}"
        )


@router.delete("/{id_empleado}",
               response_model=bool,
               summary=f"Eliminar un empleado",
               description=f"Elimina un empleado de forma logica registrado en el sistema")
def eliminar_empleado(id_empleado: int, db: Session = Depends(leer_bd)):
    if not serv_empleado.eliminar(db, id_empleado):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empleado no encontrado"
        )
    return True
