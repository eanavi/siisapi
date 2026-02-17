from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime
from app.componentes.siis1n.servicios.consulta import ServicioConsulta
from app.componentes.siis1n.esquemas.consulta import ConsultaPaginada, \
    ConsultaCreate, ConsultaResponse, ConsultaEnfermeria, ConsultaMod
from app.nucleo.baseDatos import leer_bd
from app.componentes.siis1n.modelos.consulta import Consulta
from fastapi.exceptions import HTTPException
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

@router.post("/reserva/{id_reserva}/paciente/{id_paciente}", 
             response_model=ConsultaResponse,
             summary="Registrar una nueva Consulta",
             description="Registra una nueva Consulta en el Sistema")
def crear_consulta_enfermeria(
    consulta: ConsultaEnfermeria,
    id_reserva: int,
    id_paciente: int,
    request: Request,
    db: Session = Depends(leer_bd),
    token: str = Depends(verificar_token)
    ):
    usuario = token["nombre_usuario"]
    ip = request.client.host
    consulta_creada = serv_consulta.crear_consulta_enfermeria(
        db, consulta,
        id_reserva=id_reserva,
        id_paciente=id_paciente,
        usuario_reg=usuario,
        ip_reg=ip)
    return consulta_creada

@router.get("/reserva/{id_reserva}", response_model=ConsultaResponse,
            summary=f"Obtener una consulta por su identificador",
            description=f"Obtiene una consulta por su ID")
def obtener_consulta(
        id_reserva: int,
        db: Session = Depends(leer_bd)):
    """ Obtener una consulta por su ID """
    id_consulta = db.query(Consulta.id_consulta).filter(Consulta.id_reserva == id_reserva).first()

    if id_consulta:
        return serv_consulta.leer(db, id_consulta.id_consulta)
    else:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")


    #consulta = serv_consulta.leer(db, id_reserva)
    #return consulta

@router.put("/{id_consulta}",
            response_model=ConsultaResponse,
            summary="Actualizar una consulta",
            description="Actualiza los datos de una consulta registrada en el sistema"
            )
def actualizar_consulta(
    id_consulta: int,
    consulta: ConsultaMod,
    request: Request,
    db: Session = Depends(leer_bd),
    token: str = Depends(verificar_token)
):
    """ Actualizar una consulta """
    usuario = token["nombre_usuario"]
    ip = request.client.host
    
    # Obtenemos solo los datos que fueron enviados en el request.
    # exclude_unset=True es clave aquí.
    datos_para_actualizar = consulta.model_dump(exclude_unset=True)
    datos_para_actualizar.update({"usuario_reg": usuario, "fecha_reg": datetime.now(), "ip_reg": ip, "estado_reg":"M"})
    
    # El servicio base se encarga de leer el objeto, actualizar los campos
    # del diccionario y guardar los cambios.
    consultaR = serv_consulta.actualizar(
        db, id_consulta, datos_para_actualizar)
    return consultaR