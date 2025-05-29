from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class VariableBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_prestacion: int = Field(
        ..., title="Id Prestacion",
        description="Identificador unico de la prestacion",
        json_schema_extra={"example": 1})
    for_codigo: int = Field(
        ..., title="for_codigo",
        description="Codigo de la variable en el sistema SOAPS, tabla se_formulario",
        json_schema_extra={"example": 1})
    nombre_var: str = Field(
        ..., title="Nombre Variable",
        description="Nombre de la variable",
        json_schema_extra={"example": "Nombre"})
    tipo: int = Field(
        ..., title="Tipo",
        description="Tipo de la variable, se encuentra en la lista grupo se_tipo_dato",
        json_schema_extra={"example": 1})
    unidad: Optional[str] = Field(
        ..., title="Unidad",
        description="Unidad de la variable, 1: años, 2: meses, 3: dias",
        json_schema_extra={"example": "años"})
    lis_tabla: Optional[str] = Field(
        ..., title="Lista Tabla",
        description="Lista tabla de la variable, se encuentra en la lista grupo se_lista_tabla",
        json_schema_extra={"example": "lista_tabla"})
    grupo: Optional[str] = Field(
        ..., title="Grupo",
        description="Grupo de la variable, se utiliza para la introduccion del formulario",
        json_schema_extra={"example": "grupo"})


class VariableCreate(VariableBase):
    pass


class VariableResponse(VariableBase):
    id_variable: int = Field(
        ..., title="Id Variable",
        description="Identificador unico de la variable",
        json_schema_extra={"example": 1})


class RespuestaPaginada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[VariableResponse]
