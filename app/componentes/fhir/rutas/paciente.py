from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.nucleo.baseDatos import leer_bd
from app.nucleo.seguridad import verificar_token
from fhir.resources.patient import Patient
from app.componentes.siis1n.modelos.persona import Persona
from app.componentes.siis1n.esquemas.paciente import PacientePersona
from app.componentes.siis1n.servicios.paciente import ServicioPaciente
from app.componentes.siis1n.servicios.centro import ServicioCentro
from app.componentes.fhir.mapeos.mapper import persona_a_patient_fhir

router = APIRouter(prefix='/Patient', tags=["FHIR Patient"])

@router.get("/{ci_paciente}", response_model=Patient,
summary=f"Busqueda de paciente a partir del carnet de identidad",
description=f"Desplegar los datos de un paciente almacenado en el sistema a partir del carnet de identidad"
)
def traer_paciente(ci_paciente: str, db: Session = Depends(leer_bd)):
    pacienteP = ServicioPaciente().buscar_paciente(db, ci_paciente)
    centro = ServicioCentro().leer(db, pacienteP.id_centro)

    paciente_fhir = persona_a_patient_fhir(pacienteP, centro)

    return JSONResponse(
        content=jsonable_encoder(
            paciente_fhir.model_dump(
                exclude_none=True,
                by_alias=True
            )
        )
    )   