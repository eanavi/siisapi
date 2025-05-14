from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class MenuBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_menu_padre: int = Field(
        ...,
        title="Id Menu Padre",
        description="Identificador unico del menu padre",
        json_schema_extra={"ejemplo": 1}
    )

    nombre_menu: str = Field(
        ...,
        title="Nombre",
        description="Nombre del menu",
        json_schema_extra={"ejemplo": "Menu Principal"}
    )
    ruta: str = Field(
        ...,
        title="ruta",
        description="Url del menu",
        json_schema_extra={"ejemplo": "/menu"}
    )
    icono: Optional[str] = Field(
        None,
        title="Icono",
        description="Icono del menu",
        json_schema_extra={"ejemplo": "fa fa-home"}
    )

    orden: int = Field(
        ...,
        title="Orden",
        description="Orden del menu",
        json_schema_extra={"ejemplo": 1}
    )

    categoria: str = Field(
        ...,
        title="Categoria",
        description="Categoria del menu",
        json_schema_extra={"ejemplo": "menu"}
    )
class MenuCreate(MenuBase):
    pass

class MenuResponse(MenuBase):
    model_config = ConfigDict(from_attributes=True)
    id_menu: int = Field(
        ...,
        title="Id Menu",
        description="Identificador unico del menu",
        json_schema_extra={"ejemplo": 1}
    )

class MenuPaginado(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """ """
    total: int
    pagina: int
    tamanio: int
    items: List[MenuResponse]
