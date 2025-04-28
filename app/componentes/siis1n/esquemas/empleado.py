from pydantic import BaseModel, UUID4, Field, ConfigDict
from app.componentes.siis1n.esquemas.persona import PersonaBase
from typing import Optional, List


class EmpleadoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_persona: UUID4 = Field(
        ..., title="Id Persona",
        description="Identificador unico de la persona",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"})
    tipo_empleado: str = Field(
        ..., title="Tipo de persona",
        description="Tipo de persona: 'A' = Administracion, 'M' = Medica",
        json_schema_extra={"example": "E"})
    profesion: int = Field(
        ..., title="Profesion",
        description="Identificador unico de la profesion",
        json_schema_extra={"example": 1})
    registro_profesional: Optional[str] = Field(
        None, title="Registro Profesional",
        description="Registro profesional del empleado",
        json_schema_extra={"example": "123456"})
    id_centro: int = Field(
        ..., title="Id Centro",
        description="Identificador unico del centro",
        json_schema_extra={"example": 1})
    cargo: Optional[str] = Field(
        None,
        title="Cargo",
        description="Cargo del empleado",
        json_schema_extra={"example": "Medico"})


class EmpleadoPersona(PersonaBase):
    model_config = ConfigDict(from_attributes=True)

    tipo_empleado: str = Field(
        ..., title="Tipo de persona",
        description="Tipo de persona: 'E' = Empleado, 'P' = Paciente",
        json_schema_extra={"example": "E"})
    profesion: int = Field(
        ..., title="Profesion",
        description="Identificador unico de la profesion",
        json_schema_extra={"example": 1})
    registro_profesional: Optional[str] = Field(
        None, title="Registro Profesional",
        description="Registro profesional del empleado",
        json_schema_extra={"example": "123456"})
#    id_centro: int = Field(
#        ..., title="Id Centro",
#        description="Identificador unico del centro",
#        json_schema_extra={"example": 1})
    cargo: Optional[str] = Field(
        None, title="Cargo",
        description="Cargo del empleado",
        json_schema_extra={"example": "Medico"})


class EmpleadoCreate(EmpleadoBase):
    pass


class EmpleadoResponse(EmpleadoBase):
    id_empleado: int = Field(
        ..., title="Id Empleado",
        description="Identificador unico del empleado",
        json_schema_extra={"example": 1})


class RespuestaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[EmpleadoResponse]
