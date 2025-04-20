from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict


class ListaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_grupo: int = Field(
        ...,
        title="Id Grupo",
        description="Id del Grupo",
        json_schema_extra={"exemplo": 1}
    )
    cod_texto: str = Field(
        ...,
        title="Codigo de Texto",
        description="Codigo de texto de la lista",
        json_schema_extra={"example": "LP"})
    cod_numero: int = Field(
        ...,
        title="Codigo Numerico",
        description="Codigo numerico de la lista",
        json_schema_extra={"example": 1})
    descripcion: str = Field(
        ...,
        title="Descripcion",
        description="Descripcion de la lista",
        json_schema_extra={"example": "La Paz"})
    orden: int = Field(
        ...,
        title="Orden",
        description="Orden de la lista",
        json_schema_extra={"example": 1})


class ListaCreate(ListaBase):
    pass


class ListaResponse(ListaBase):
    id_lista: int = Field(
        ...,
        title="Id Lista",
        description="Identificador unico de la lista",
        json_schema_extra={"example": 1})


class ListaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo: str = Field(
        ...,
        title=f"Codigo Lista",
        description=f"Identificador de la lista",
        json_schema_extra={"ejemplo": 1}
    )
    descripcion: str = Field(
        ...,
        title="Descripcion",
        description="Descripcion de la lista",
        json_schema_extra={"example": "La Paz"}
    )


class RespuestaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[ListaResponse]
