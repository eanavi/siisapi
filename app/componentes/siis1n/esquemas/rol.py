from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class RolBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre_rol: str = Field(
        ..., title="Nombre",
        description="Nombre del rol",
        json_schema_extra={"example": "Administrador"})
    descripcion: Optional[str] = Field(
        None, title="Descripcion",
        description="Descripcion del rol",
        json_schema_extra={"example": "Rol con todos los permisos"})


class RolCreate(RolBase):
    pass


class RolResponse(RolBase):
    id_rol: int = Field(
        ..., title="Id Rol",
        description="Identificador unico del rol",
        json_schema_extra={"example": 1})


class RespuestaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[RolResponse]
