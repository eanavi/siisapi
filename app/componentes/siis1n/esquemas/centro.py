from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class CentroBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo_snis: int = Field(
        ..., title="Codigo SNIS",
        description="Codigo SNIS del centro",
        json_schema_extra={"example": 1})
    nombre: str = Field(
        ..., title="Nombre",
        description="Nombre del centro",
        json_schema_extra={"example": "Hospital Obrero Nº 1"})
    direccion: Optional[str] = Field(
        None, title="Direccion IP", description="Direccion ip de la base de datos",
        json_schema_extra={"example": "192.168.70.25"})
    usuario: Optional[str] = Field(
        None, title="Usuario", description="Usuario de la base de datos",
        json_schema_extra={"example": "postgres"})
    clave: Optional[str] = Field(
        None, title="Clave", description="Clave de acceso a la base de datos",
        json_schema_extra={"example": "123456"})
    puerto: Optional[int] = Field(
        None, title="Puerto", description="Puerto de la base de datos",
        json_schema_extra={"example": 5432})


class CentroCreate(CentroBase):
    pass


class CentroResponse(CentroBase):
    id_centro: int = Field(..., title="Id Centro",
                           description="Identificador unico del centro",
                           json_schema_extra={"example": 1})


class CentroPaginado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[CentroResponse]
