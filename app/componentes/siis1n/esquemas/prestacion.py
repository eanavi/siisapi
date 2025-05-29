from pydantic import BaseModel, Field, ConfigDict
from app.componentes.siis1n.esquemas.edad_pydantic import EdadPydantic
from typing import Optional, List


class PrestacionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_centro: int = Field(
        ..., title="Id Centro",
        description="Identificador unico del centro",
        json_schema_extra={"example": 1})
    nombre_prestacion: str = Field(
        ..., title="Nombre",
        description="Nombre de la prestacion",
        json_schema_extra={"example": "Consulta Medica"})
    sigla: str = Field(
        ..., title="Sigla",
        description="Sigla de la prestacion",
        json_schema_extra={"example": "CM"})
    edad_maxima: Optional[EdadPydantic] = Field(
        None, title="Edad Maxima",
        description="Edad maxima para la prestacion",
        json_schema_extra={"example": {"anio": 18, "mes": 0, "dia": 0}})
    edad_minima: Optional[EdadPydantic] = Field(
        None, title="Edad Minima",
        description="Edad minima para la prestacion",
        json_schema_extra={"example": {"anio": 60, "mes": 0, "dia": 0}})
    genero: Optional[str] = Field(
        None, title="Genero",
        description="Genero para la prestacion",
        json_schema_extra={"example": "M"})
    tipo_prestador: Optional[str] = Field(
        None, title="Tipo de Prestador",
        description="Tipo de prestador para la prestacion",
        json_schema_extra={"example": "P"})
    tiempo_maximo: Optional[int] = Field(
        None, title="Tiempo Maximo",
        description="Tiempo maximo para la prestacion",
        json_schema_extra={"example": 30})


class PrestacionCreate(PrestacionBase):
    pass


class PrestacionResponse(PrestacionBase):
    model_config = ConfigDict(from_attributes=True)
    id_prestacion: int = Field(
        ..., title="Id Prestacion",
        description="Identificador unico de la prestacion",
        json_schema_extra={"example": 1})


class PrestacionPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """ """
    total: int
    pagina: int
    tamanio: int
    items: List[PrestacionResponse]
