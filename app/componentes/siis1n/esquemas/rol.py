from pydantic import BaseModel, Field
from typing import Optional

class RolBase(BaseModel):
    nombre : str = Field(..., example="Administrador", title="Nombre", description="Nombre del rol")
    descripcion : Optional[str] = Field(None, example="Rol con todos los permisos", title="Descripcion", description="Descripcion del rol")

class RolCreate(RolBase):
    pass

class RolResponse(RolBase):
    id_rol : int = Field(..., example=1, title="Id Rol", description="Identificador unico del rol")
    
    class Config:
        from_atributes = True
