from pydantic import BaseModel, Field, ConfigDict
from typing import List


class GrupoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre_grupo: str = Field(
        ...,
        title="Nombre",
        description="Nombre del Grupo",
        json_schema_extra={"ejemplo": "estado_civil"}
    )
    tipo: str = Field(
        ...,
        title=f"Tipo",
        description=f"Tipo de grupo 'N'=numerico, 'T'=texto",
        json_schema_extra={"ejemplo": "A"}
    )
    area: str = Field(
        ...,
        title=f"Area",
        description=f"Area del grupo 'M'=medica, 'A'=administracion",
        json_schema_extra={"ejemplo": "M"}
    )


class GrupoCreate(GrupoBase):
    pass


class GrupoResponse(GrupoBase):
    id_grupo: int = Field(
        ...,
        title=f"Id Grupo",
        description=f"Iden,tificador unico del grupo",
        json_schema_extra={"ejemplo": 11}
    )


class ListaGrupo(BaseModel):
    codigo: str = Field(
        ...,
        title=f"codigo",
        description=f"Codigo de la lista",
        json_schema_extra={"ejemplo": "1"},
    )
    descripcion: str = Field(
        ...,
        title=f"descripcion",
        description=f"Descripcion del tipo de la lista",
        json_schema_extra={"ejemplo": "La Paz"},
    )


class GrupoPaginado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    pagina: int
    tamanio: int
    items: List[GrupoResponse]
