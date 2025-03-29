from pydantic import BaseModel, UUID4, Field
from app.componentes.siis1n.esquemas.persona import PersonaBase
from typing import Optional, List


class EmpleadoBase(BaseModel):
    id_persona: UUID4 = Field(..., example="123e4567-e89b-12d3-a456-426614174000",
                              title="Id Persona", description="Identificador unico de la persona")
    tipo_empleado: str = Field(..., example="E", title="Tipo de persona",
                               description="Tipo de persona: 'A' = Administracion, 'M' = Medica")
    profesion: int = Field(..., example=1, title="Profesion",
                           description="Identificador unico de la profesion")
    registro_profesional: Optional[str] = Field(None, example="123456",
                                                title="Registro Profesional",
                                                description="Registro profesional del empleado")
    id_centro: int = Field(..., example=1, title="Id Centro",
                           description="Identificador unico del centro")
    cargo: Optional[str] = Field(None, example="Medico", title="Cargo",
                                 description="Cargo del empleado")


class EmpleadoPersona(PersonaBase):
    tipo_empleado: str = Field(..., example="E", title="Tipo de persona",
                               description="Tipo de persona: 'E' = Empleado, 'P' = Paciente")
    profesion: int = Field(..., example=1, title="Profesion",
                           description="Identificador unico de la profesion")
    registro_profesional: Optional[str] = Field(None, example="123456",
                                                title="Registro Profesional",
                                                description="Registro profesional del empleado")
    id_centro: int = Field(..., example=1, title="Id Centro",
                           description="Identificador unico del centro")
    cargo: Optional[str] = Field(None, example="Medico", title="Cargo",
                                 description="Cargo del empleado")

    class Config:
        from_attributes = True


class EmpleadoCreate(EmpleadoBase):
    pass


class EmpleadoResponse(EmpleadoBase):
    id_empleado: int = Field(..., example=1, title="Id Empleado",
                             description="Identificador unico del empleado")

    class Config:
        from_atributes = True


class RespuestaPaginada(BaseModel):
    total: int
    pagina: int
    tamanio: int
    items: List[EmpleadoResponse]
