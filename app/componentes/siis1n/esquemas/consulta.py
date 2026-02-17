from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class ConsultaEnfermeria(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_reserva: int = Field(
        ..., title="Id Reserva",
        description="Identificador de la reserva", 
        json_schema_extra={"example": 1}
    )
    id_medico: Optional[int] = Field(
        None, title="Id Médico", 
        description="Identificador del médico",
        json_schema_extra={"example": 2}
    )

    id_enfermera: Optional[int] = Field(
        None, title="Id Enfermera", 
        description="Identificador de la enfermera", 
        json_schema_extra={"example": 3}
    )
    fecha: datetime = Field(
        ..., title="Fecha de Consulta",
        description="Fecha y hora de la consulta", 
        json_schema_extra={"example": "2025-05-12T14:30:00"}
    )
    peso: Optional[Decimal] = Field(
        None, title="Peso", 
        description="Peso del paciente", 
        json_schema_extra={"example": 70.5}
    )
    talla: Optional[Decimal] = Field(
        None, title="Talla", 
        description="Talla del paciente", 
        json_schema_extra={"example": 1.75}
    )
    temperatura: Optional[Decimal] = Field(
        None, title="Temperatura", 
        description="Temperatura del paciente", 
        json_schema_extra={"example": 37.0}
    )
    presion: Optional[str] = Field(
        None, title="Presión Arterial", 
        description="Presión arterial del paciente", 
        json_schema_extra={"example": "120/80"}
    )
    frecuencia_cardiaca: Optional[int] = Field(
        None, title="Frecuencia Cardiaca", 
        description="Frecuencia cardiaca del paciente", 
        json_schema_extra={"example": 80}
    )
    frecuencia_respiratoria: Optional[int] = Field(
        None, title="Frecuencia Respiratoria", 
        description="Frecuencia respiratoria del paciente", 
        json_schema_extra={"example": 16}
    )
    saturacion: Optional[Decimal] = Field(
        None, title="Saturación de Oxígeno", 
        description="Saturación de oxígeno del paciente", 
        json_schema_extra={"example": 98.0}
    )
    inyectables: Optional[int] = Field(
        None, title="Inyectables", 
        description="Número de inyectables aplicados", 
        json_schema_extra={"example": 1}
    )
    sueros: Optional[int] = Field(
        None, title="Sueros", 
        description="Número de sueros administrados", 
        json_schema_extra={"example": 0}
    )
    curaciones: Optional[int] = Field(
        None, title="Curaciones", 
        description="Número de curaciones realizadas", 
        json_schema_extra={"example": 1}
    )
    otras_enf: Optional[int] = Field(
        None, title="Otras Enfermedades", 
        description="Número de otras enfermedades", 
        json_schema_extra={"example": 0}
    )

class ConsultaMod(BaseModel):
    motivo: Optional[str] = Field(
        None, title="Motivo de Consulta", 
        description="Motivo de la consulta", 
        json_schema_extra={"example": "Dolor de cabeza"}
    )
    ex_fisico: Optional[str] = Field(
        None, title="Examen Físico", 
        description="Resultado del examen físico", 
        json_schema_extra={"example": "Paciente alerta y orientado"}
    )
    diagnostico: Optional[str] = Field(
        None, title="Diagnóstico", 
        description="Diagnóstico de la consulta", 
        json_schema_extra={"example": "Cefalea"}
    )
    tratamiento: Optional[str] = Field(
        None, title="Tratamiento", 
        description="Tratamiento indicado", 
        json_schema_extra={"example": "Paracetamol 500mg"}
    )
    dx_cie10: Optional[List[Optional[str]]] = Field(
        None, title="Diagnósticos CIE-10", 
        description="Lista de códigos CIE-10", 
        json_schema_extra={"example": ["R51"]}
    )
    mortalidad: Optional[str] = Field(
        None, title="Mortalidad", 
        description="Indicador de mortalidad", 
        json_schema_extra={"example": "N"}
    )
    referencia: Optional[int] = Field(
        None, title="Referencia", 
        description="ID de referencia si aplica", 
        json_schema_extra={"example": 4}
    )
    subsidio: Optional[int] = Field(
        None, title="Subsidio", 
        description="Indicador de subsidio", 
        json_schema_extra={"example": 0}
    )
    observaciones: Optional[str] = Field(
        None, title="Observaciones", 
        description="Observaciones adicionales", 
        json_schema_extra={"example": "Seguimiento en 7 días"}
    )

class ConsultaBase(ConsultaEnfermeria):
    model_config = ConfigDict(from_attributes=True)

    motivo: Optional[str] = Field(
        None, title="Motivo de Consulta", 
        description="Motivo de la consulta", 
        json_schema_extra={"example": "Dolor de cabeza"}
    )
    ex_fisico: Optional[str] = Field(
        None, title="Examen Físico", 
        description="Resultado del examen físico", 
        json_schema_extra={"example": "Paciente alerta y orientado"}
    )
    diagnostico: Optional[str] = Field(
        None, title="Diagnóstico", 
        description="Diagnóstico de la consulta", 
        json_schema_extra={"example": "Cefalea"}
    )
    tratamiento: Optional[str] = Field(
        None, title="Tratamiento", 
        description="Tratamiento indicado", 
        json_schema_extra={"example": "Paracetamol 500mg"}
    )
    dx_cie10: Optional[List[Optional[str]]] = Field(
        None, title="Diagnósticos CIE-10", 
        description="Lista de códigos CIE-10", 
        json_schema_extra={"example": ["R51"]}
    )
    mortalidad: Optional[str] = Field(
        None, title="Mortalidad", 
        description="Indicador de mortalidad", 
        json_schema_extra={"example": "N"}
    )
    referencia: Optional[int] = Field(
        None, title="Referencia", 
        description="ID de referencia si aplica", 
        json_schema_extra={"example": 4}
    )
    subsidio: Optional[int] = Field(
        None, title="Subsidio", 
        description="Indicador de subsidio", 
        json_schema_extra={"example": 0}
    )
    observaciones: Optional[str] = Field(
        None, title="Observaciones", 
        description="Observaciones adicionales", 
        json_schema_extra={"example": "Seguimiento en 7 días"}
    )



class ConsultaCreate(ConsultaBase):
    pass

class ConsultaResponse(ConsultaBase):
    id_consulta: int = Field(
        ..., title="Id Consulta", 
        description="Identificador único de la consulta", 
        json_schema_extra={"example": 1}
    )

class ConsultaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """ """
    total: int
    pagina: int
    tamanio: int
    items: List[ConsultaResponse]