from pydantic import BaseModel, UUID4, Field, ConfigDict
from app.componentes.siis1n.esquemas.persona import PersonaBase, Direccion, DireccionTipo
from typing import Optional, List, Dict
from datetime import date, time

class PacienteBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_persona: UUID4 = Field(
        ..., title="Id Persona",
        description="Identificador unico de la persona",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"})
    id_centro: int = Field(
        ..., title="Id Centro",
        description="Identificador unico del centro",
        json_schema_extra={"example": 1})
    estado_civil: str = Field(
        ..., title="Estado Civil",
        description="Estado civil del paciente",
        json_schema_extra={"example": "SO"})
    tipo_sangre: Optional[str] = Field(
        None, title="Tipo de Sangre",
        description="Tipo de sangre del paciente",
        json_schema_extra={"example": "O+"})
    ocupacion: Optional[int] = Field(
        None, title="Ocupacion",
        description="Ocupacion del paciente",
        json_schema_extra={"example": 1})
    nivel_estudios: Optional[int] = Field(
        None, title="Nivel de Estudios",
        description="Nivel de estudios del paciente",
        json_schema_extra={"example": 1})
    mun_nacimiento: int = Field(
        ..., title="Municipio de Nacimiento",
        description="Municipio de nacimiento del paciente",
        json_schema_extra={"example": 1})
    mun_residencia: int = Field(
        ..., title="Municipio de Residencia",
        description="Municipio de residencia del paciente",
        json_schema_extra={"example": 1})
    idioma_hablado: int = Field(
        ..., title="Idioma Hablado",
        description="Idioma hablado por el paciente",
        json_schema_extra={"example": 1})
    idioma_materno: int = Field(
        ..., title="Idioma Materno",
        description="Idioma materno del paciente",
        json_schema_extra={"example": 1})
    autopertenencia: int = Field(
        ..., title="Autopertenencia",
        description="Autopertenencia del paciente",
        json_schema_extra={"example": 1})
    gestion_comunitaria: Optional[str] = Field(
        None, title="Gestion Comunitaria",
        description="Gestion comunitaria del paciente",
        json_schema_extra={"example": "Gestion comunitaria"})


class PacientePersona(PersonaBase):
    model_config = ConfigDict(from_attributes=True)

#    id_centro: int = Field(
#        ..., title="Id Centro",
#        description="Identificador unico del centro",
#        json_schema_extra={"example": 1})
    estado_civil: str = Field(
        ..., title="Estado Civil",
        description="Estado civil del paciente",
        json_schema_extra={"example": "SO"})
    tipo_sangre: Optional[str] = Field(
        None, title="Tipo de Sangre",
        description="Tipo de sangre del paciente",
        json_schema_extra={"example": "O+"})
    ocupacion: Optional[int] = Field(
        None, title="Ocupacion",
        description="Ocupacion del paciente",
        json_schema_extra={"example": 1})
    nivel_estudios: Optional[int] = Field(
        None, title="Nivel de Estudios",
        description="Nivel de estudios del paciente",
        json_schema_extra={"example": 1})
    idioma_hablado: int = Field(
        ..., title="Idioma Hablado",
        description="Idioma hablado por el paciente",
        json_schema_extra={"example": 1})
    idioma_materno: int = Field(
        ..., title="Idioma Materno",
        description="Idioma materno del paciente",
        json_schema_extra={"example": 1})
    autopertenencia: int = Field(
        ..., title="Autopertenencia",
        description="Autopertenencia del paciente",
        json_schema_extra={"example": 1})
    gestion_comunitaria: Optional[str] = Field(
        None, title="Gestion Comunitaria",
        description="Gestion comunitaria del paciente",
        json_schema_extra={"example": "Gestion comunitaria"})


class PacienteListado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_paciente: int = Field(
        ..., title="Id Paciente",
        description="Identificador unico del paciente",
        json_schema_extra={"example": 1})
    id_reserva: int = Field(
        ..., title="Id Reserva",
        description="Identificador unico de la reserva",
        json_schema_extra={"example": 1}
    )
    ci: str = Field(
        ..., title="CI",
        description="Cedula de identidad del paciente",
        json_schema_extra={"example": "12345678"})
    paterno: str = Field(
        ..., title="Apellido Paterno",
        description="Apellido paterno del paciente",
        json_schema_extra={"example": "Perez"})
    materno: str = Field(
        ..., title="Apellido Materno",
        description="Apellido materno del paciente",
        json_schema_extra={"example": "Lopez"})
    nombres: str = Field(
        ..., title="Nombres",
        description="Nombres del paciente",
        json_schema_extra={"example": "Juan Carlos"})
    edad: str = Field(
        ..., title="Edad",
        description="Edad del paciente en años",
        json_schema_extra={"example": 30})
    sexo: str = Field(
        ..., title="Sexo",
        description="Sexo del paciente",
        json_schema_extra={"example": "M"}
    )
    fecha_reserva: Optional[date] = Field(
        None, title="Fecha de Reserva",
        description="Fecha de reserva del paciente",
        json_schema_extra={"example": "2023-10-01T12:00:00Z"})
    hora_reserva: Optional[time] = Field(
        None, title="Hora de Reserva",
        description="Hora de reserva del paciente",
        json_schema_extra={"example": "08:00:00"})

class PacienteB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_persona: UUID4 = Field(
        ..., title="Id Persona",
        description="Identificador unico de la persona",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"})
    id_paciente: int = Field(
        ..., title="Id Paciente",
        description="Identificador unico del paciente",
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

class PacienteResponse(PacientePersona):
    model_config = ConfigDict(from_attributes=True)

    id_paciente: int = Field(
        ..., title="Id Paciente",
        description="Identificador unico del paciente",
        json_schema_extra={"example": 1})


class RespuestaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[PacienteResponse]
