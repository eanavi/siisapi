from pydantic import BaseModel, UUID4, Field, ConfigDict
from uuid import UUID
from datetime import date
from typing import Optional, List, Dict


class Direccion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    zona: str = Field(..., title="Zona", description="Zona de la direccion",
                      json_schema_extra={"example": "Villa Dolores"})
    calle: str = Field(..., title="Calle", description="Calle de la direccion",
                       json_schema_extra={"example": "Av. 6 de Agosto"})
    numero: str = Field(..., title="Numero", description="Numero de la direccion",
                        json_schema_extra={"example": "123"})
    ciudad: str = Field(..., title="Ciudad", description="Ciudad de la direccion",
                        json_schema_extra={"example": "La Paz"})


class DireccionTipo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: str = Field(..., title="Tipo de Direccion",
                      description="Tipo de direccion",
                      json_schema_extra={"example": "personal"})
    direccion: Direccion = Field(..., title="Direccion",
                                 description="Direccion de la persona")


class PersonaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
        json_schema_extra={"example": {"tipo": "personal", "numero": "7777777"}})
    correo: Optional[Dict[str, str]] = Field(
        None, title="Correo", description="Correo electronico de la persona",
        json_schema_extra={"example": {"tipo": "personal", "correo": "mendoza@gmail.com"}})


class PersonaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_persona: UUID4 = Field(
        ..., title="Id Persona",
        description="Identificador unico de la persona",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"})
    tipo: str = Field(
        ..., title="Tipo de persona",
        description="Tipo de persona: 'E' = Empleado, 'P' = Paciente",
        json_schema_extra={"example": "E"})
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
        ..., title="Nombres", description="Nombres de la persona",
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
        json_schema_extra={"example": [{"tipo": "personal", "direccion":
                                        {"zona": "Villa Dolores", "calle": "Av. 6 de Agosto", "numero": "123"}}]})
    telefono: Optional[Dict[str, str]] = Field(
        None, title="Telefono",
        description="Numero de telefono de la persona",
        json_schema_extra={"example": {"tipo": "personal", "numero": "7777777"}})
    correo: Optional[Dict[str, str]] = Field(
        None, title="Correo",
        description="Correo electronico de la persona",
        json_schema_extra={"example": {"tipo": "personal", "correo": "mendoza@gmail.com"}})


class PersonaCreate(PersonaBase):
    pass


class PersonaLista(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_persona: str = Field(
        ..., title="Id Persona",
        description="Identificador unico de la persona",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"})
    tipo: str = Field(
        ..., title="Tipo de persona",
        description="Tipo de persona: 'E' = Empleado, 'P' = Paciente",
        json_schema_extra={"example": "E"})
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
    procedencia: str = Field(
        ..., title="Centro de Salud de procedencia",
        description="Centro de Salud donde estan registrados los datos del paciente",
        json_schema_extra={"example": "propio"})


class RespuestaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[PersonaLista]
