from pydantic import BaseModel, Field
from typing import Optional, List


class CentroBase(BaseModel):
    codigo_snis: int = Field(..., example=1, title="Codigo SNIS",
                             description="Codigo SNIS del centro")
    nombre: str = Field(..., example="Hospital Obrero Nº 1", title="Nombre",
                        description="Nombre del centro")
    direccion: Optional[str] = Field(None, example="192.168.70.25",
                                     title="Direccion IP", description="Direccion ip de la base de datos")
    usuario: Optional[str] = Field(None, example="postgres", title="Usuario",
                                   description="Usuario de la base de datos")
    clave: Optional[str] = Field(None, example="123456", title="Clave",
                                 description="Clave de acceso a la base de datos")
    puerto: Optional[int] = Field(
        None,
        example=5432, title="Puerto",
        description="Puerto de la base de datos")


class CentroCreate(CentroBase):
    pass


class CentroResponse(CentroBase):
    id_centro: int = Field(..., example=1, title="Id Centro",
                           description="Identificador unico del centro")

    class Config:
        from_attributes = True


class CentroPaginado(BaseModel):
    total: int
    pagina: int
    tamanio: int
    items: List[CentroResponse]
