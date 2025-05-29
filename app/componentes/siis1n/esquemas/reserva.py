from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ReservaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_turno: int = Field(
        ..., title="Id Turno",
        description="Identificador unico del turno",
        json_schema_extra={"example": 1})
    id_paciente: int = Field(
        ..., title="Id Paciente",
        description="Identificador unico del paciente",
        json_schema_extra={"example": 1})
    fecha_reserva: str = Field(
        ..., title="Fecha Reserva",
        description="Fecha de reserva del turno",
        json_schema_extra={"example": "2023-01-01"})
    hora_reserva: str = Field(
        ..., title="Hora Reserva",
        description="Hora de reserva del turno",
        json_schema_extra={"example": "08:00:00"})


class ReservaCreate(ReservaBase):
    pass


class ReservaResponse(ReservaBase):
    id_reserva: int = Field(
        ..., title="Id Reserva",
        description="Identificador unico de la reserva",
        json_schema_extra={"example": 1})


class RespuestaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[ReservaResponse]
