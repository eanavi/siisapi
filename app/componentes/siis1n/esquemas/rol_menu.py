from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class RolMenuBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_rol: int = Field(
        ...,
        title="Id Rol",
        description="Identificador unico del rol",
        json_schema_extra={"ejemplo": 1}
    )
    id_menu: int = Field(
        ...,
        title="Id Menu",
        description="Identificador unico del menu",
        json_schema_extra={"ejemplo": 1}
    )

    metodo: str = Field(
        ...,
        title="Metodo",
        description="Metodo del menu",
        json_schema_extra={"ejemplo": "GET"}
    )

class RolMenuCreate(RolMenuBase):
    pass

class RolMenuResponse(RolMenuBase):
    model_config = ConfigDict(from_attributes=True)
    id_rol_menu: int = Field(
        ...,
        title="Id Rol Menu",
        description="Identificador unico del rol menu",
        json_schema_extra={"ejemplo": 1}
    )

class RolMenuPaginado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[RolMenuResponse]
