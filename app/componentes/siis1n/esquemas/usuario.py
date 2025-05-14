from pydantic import BaseModel, UUID4, Field, ConfigDict
from typing import Optional, List


class UsurioBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre_usuario: str = Field(
        ..., title="Nombre de Usuario",
        description="Nombre de usuario",
        json_schema_extra={"example": "rmendoza"})


class UsuarioCreate(UsurioBase):
    clave: str = Field(
        ..., title="Clave",
        description="Clave de acceso del usuario",
        json_schema_extra={"example": "123456"})
    id_persona: UUID4 = Field(
        ..., title="Id Persona",
        description="Identificador unico de la persona",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"})
    id_rol: int = Field(
        ..., title="Id Rol",
        description="Identificador unico del rol",
        json_schema_extra={"example": 1})
    id_empleado: Optional[int] = Field(
        None, title="Id Empleado",
        description="Identificador unico del empleado",
        json_schema_extra={"example": 1})


class UsuarioExt(BaseModel):
    nombre_persona: str = Field(
        ..., title="Nombre de Persona",
        description="Nombre completo de la persona",
        json_schema_extra={"example": "Rafael Mendoza"})
    cargo: str = Field(
        ..., title="Cargo",
        description="Cargo del usuario",
        json_schema_extra={"example": "Medico Ginecologo"})
    rol: str = Field(
        ..., title="Rol",
        description="Nombre del rol del usuario",
        json_schema_extra={"example": "Administrador"})


class UsuarioResponse(UsurioBase):
    id_usuario: int = Field(
        ..., title="Id Usuario",
        description="Identificador unico del usuario",
        json_schema_extra={"example": 1})
    id_persona: UUID4 = Field(
        ..., title="Id Persona",
        description="Identificador unico de la persona",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"})


class RespuestaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[UsuarioResponse]
