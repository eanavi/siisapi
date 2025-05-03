from pydantic import BaseModel, UUID4, Field, ConfigDict
from app.componentes.siis1n.esquemas.persona import PersonaBase
from typing import Optional, List


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
