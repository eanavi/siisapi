from pydantic import BaseModel, UUID4, Field
from typing import Optional


class UsurioBase(BaseModel):
    nombre_usuario: str = Field(..., example="rmendoza",
                                title="Nombre de Usuario", description="Nombre de usuario")


class UsuarioCreate(UsurioBase):
    clave: str = Field(..., example="123456", title="Clave",
                       description="Clave de acceso del usuario")
    id_persona: UUID4 = Field(..., example="123e4567-e89b-12d3-a456-426614174000",
                              title="Id Persona", description="Identificador unico de la persona")
    id_rol: int = Field(..., example=1, title="Id Rol",
                        description="Identificador unico del rol")
    id_empleado: Optional[int] = Field(
        None, example=1, title="Id Empleado", description="Identificador unico del empleado")


class UsuarioResponse(UsurioBase):
    id_usuario: int = Field(..., example=1, title="Id Usuario",
                            description="Identificador unico del usuario")
    id_persona: UUID4 = Field(..., example="123e4567-e89b-12d3-a456-426614174000",
                              title="Id Persona", description="Identificador unico de la persona")

    class Config:
        from_atributes = True
