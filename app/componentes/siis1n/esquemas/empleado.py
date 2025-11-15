from pydantic import BaseModel, UUID4, Field, ConfigDict
from app.componentes.siis1n.esquemas.persona import PersonaBase
from app.componentes.siis1n.esquemas.persona import DireccionTipo, Direccion
from typing import Optional, List, Dict
from datetime import date, time

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

class EmpleadoB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_persona: UUID4 = Field(
        ..., title="Id Persona",
        description="Identificador unico de la persona",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"})
    id_empleado: int = Field(
        ..., title="Id Empleado",
        description="Identificador unico del empleado",
        json_schema_extra={"example": 1})
    tipo: str = Field(
        ...,
        title="Tipo de persona",
        description="Tipo de persona: 'E' = Empleado, 'P' = Paciente")
    ci: Optional[str] = Field(
        None, title="Carnet de Identidad",
        description="Numero de carnet de identidad",
        json_schema_extra={"example": "548732"})
    paterno: Optional[str] = Field(
        None, title="Apellido Paterno",
        description="Apellido paterno de la persona",
        json_schema_extra={"example": "Fernández"})
    materno: Optional[str] = Field(
        None, title="Apellido Materno",
        description="Apellido materno de la persona",
        json_schema_extra={"example": "Pérez"})
    nombres: str = Field(
        ..., title="Nombres",
        description="Nombres de la persona",
        json_schema_extra={"example": "Juan Antonio"})
    fecha_nacimiento: date = Field(
        ..., title="Fecha de Nacimiento",
        description="Fecha de nacimiento de la persona",
        json_schema_extra={"example": "1990-01-01"})
    sexo: str = Field(
        ..., title="Sexo",
        description="Sexo de la persona: 'M' = Masculino, 'F' = Femenino",
        json_schema_extra={"example": "M"})
    direccion: Optional[List[DireccionTipo]] = Field(
        None, title="Direccion",
        description="Direccion de la persona",
        json_schema_extra={"example": [{"tipo": "personal", "direccion": {"zona": "Villa Dolores", "calle": "Av. 6 de Agosto", "numero": "123"}}]})
    telefono: Optional[Dict[str, str]] = Field(
        None, title="Telefono", description="Numero de telefono de la persona",
        json_schema_extra={"example": {"celular": "62418210", "fijo": "987654321"}})
    correo: Optional[Dict[str, str]] = Field(
        None, title="Correo", description="Correo electronico de la persona",
        json_schema_extra={"example": {"personal": "correo@gmail.com", "domicilio": "correo_altern@hotmail.com"}})

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
