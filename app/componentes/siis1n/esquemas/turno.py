from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, time
from ..modelos.turno import DiaSemana



class TurnoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_medico: int = Field(
        ..., title="Id Medico",
        description="Identificador unico del medico",
        json_schema_extra={"example": 1})
    id_prestacion: int = Field(
        ..., title="Id Prestacion",
        description="Identificador unico de la prestacion",
        json_schema_extra={"example": 1})
    fecha_inicio: date = Field(
        ..., title="Fecha Inicio",
        description="Fecha de inicio del turno",
        json_schema_extra={"example": "2023-01-01"})
    fecha_final: date = Field(
        ..., title="Fecha Final",
        description="Fecha de fin del turno",
        json_schema_extra={"example": "2023-01-01"})
    hora_inicio: time = Field(
        ..., title="Hora Inicio",
        description="Hora de inicio del turno",
        json_schema_extra={"example": "08:00:00"})
    hora_final: time = Field(
        ..., title="Hora Final",
        description="Hora de fin del turno",
        json_schema_extra={"example": "17:00:00"})
    dia_semana: List[DiaSemana] = Field(
        ..., title="Dias Semana",
        description="Vector de los días de la semana del turno ('L', 'M', 'I', 'J', 'V', 'S', 'D')",
        json_schema_extra={"example": ["L", "I", "V"]})


class TurnoCreate(TurnoBase):
    pass


class TurnoResponse(TurnoBase):
    id_turno: int = Field(
        ..., title="Id Turno",
        description="Identificador unico del turno",
        json_schema_extra={"example": 1})


class RespuestaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[TurnoResponse]

class TurnoFecha(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_turno: int = Field(
        ..., title="Id Turno",
        description="Identificador unico del turno",
        json_schema_extra={"example": 1}
    )
    id_medico: int = Field(
        ..., title="Id Medico",
        description="Identificador unico del medico",
        json_schema_extra={"example": 1})
    dia_semana: str = Field(
        ..., title="Dia Semana",
        description="Dia de la semana del turno ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo')",
        json_schema_extra={"example": "L"})
    fecha_calendario: date = Field(
        ..., title="Fecha Calendario",
        description="Fecha del calendario del turno",
        json_schema_extra={"example": "2023-01-01"})
    hora_inicio: time = Field(
        ..., title="Hora Inicio",
        description="Hora de inicio del turno",
        json_schema_extra={"example": "08:00:00"})
    hora_final: time = Field(
        ..., title="Hora Final",
        description="Hora de fin del turno",
        json_schema_extra={"example": "17:00:00"})