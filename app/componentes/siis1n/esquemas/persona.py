from pydantic import BaseModel, UUID4, Field
from uuid import UUID
from datetime import date
from typing import Optional, List, Dict


class Direccion(BaseModel):
    zona : str = Field(..., example="Villa Dolores", title="Zona", description="Zona de la direccion")
    calle : str = Field(..., example="Av. 6 de Agosto", title="Calle", description="Calle de la direccion")
    numero : str = Field(..., example="123", title="Numero", description="Numero de la direccion")
    ciudad: str = Field(..., example="La Paz", title="Ciudad", description="Ciudad de la direccion")

class DireccionTipo(BaseModel):
    tipo : str = Field(..., example="personal", title="Tipo de Direccion", description="Tipo de direccion")
    direccion : Direccion = Field(..., title="Direccion", description="Direccion de la persona")

class PersonaBase(BaseModel):
    tipo : str = Field(..., title="Tipo de persona", description="Tipo de persona: 'E' = Empleado, 'P' = Paciente")
    ci : Optional[str] = Field(None, example="548732", title="Carnet de Identidad", description="Numero de carnet de identidad")
    paterno : Optional[str] = Field(None, example="Fernández", title="Apellido Paterno", description="Apellido paterno de la persona")
    materno : Optional[str] = Field(None, example="Pérez", title="Apellido Materno", description="Apellido materno de la persona")
    nombres : str = Field(..., example="Juan Antonio", title="Nombres", description="Nombres de la persona")
    fecha_nacimiento : date = Field(..., example="1990-01-01", title="Fecha de Nacimiento", description="Fecha de nacimiento de la persona")
    sexo : str = Field(..., example="M", title="Sexo", description="Sexo de la persona: 'M' = Masculino, 'F' = Femenino")
    direccion : Optional[List[DireccionTipo]] = Field(None, example=[{"tipo":"personal", 
                                                                      "direccion":{"zona":"Villa Dolores","calle":"Av. 6 de Agosto","numero":"123"}}], 
                                                      title="Direccion", description="Direccion de la persona")
    telefono : Optional[Dict[str, str]] = Field(None, example={"tipo":"personal", "numero":"7777777"}, 
                                            title="Telefono", description="Numero de telefono de la persona")
    correo : Optional[Dict[str,str]] = Field(None, example={"tipo":"personal", "correo":"mendoza@gmail.com"},
                                          title="Correo", description="Correo electronico de la persona")
    
    class Config:
        from_atributes = True

class PersonaResponse(BaseModel):
    id_persona : UUID4 = Field(..., example="123e4567-e89b-12d3-a456-426614174000", title="Id Persona", description="Identificador unico de la persona")
    tipo : str = Field(..., example="E", title="Tipo de persona", description="Tipo de persona: 'E' = Empleado, 'P' = Paciente")
    ci : Optional[str] = Field(None, example="548732", title="Carnet de Identidad", description="Numero de carnet de identidad")
    paterno : Optional[str] = Field(None, example="Fernández", title="Apellido Paterno", description="Apellido paterno de la persona")
    materno : Optional[str] = Field(None, example="Pérez", title="Apellido Materno", description="Apellido materno de la persona")
    nombres : str = Field(..., example="Juan Antonio", title="Nombres", description="Nombres de la persona")
    fecha_nacimiento : date = Field(..., example="1990-01-01", title="Fecha de Nacimiento", description="Fecha de nacimiento de la persona")
    sexo : str = Field(..., example="M", title="Sexo", description="Sexo de la persona: 'M' = Masculino, 'F' = Femenino")
    direccion : Optional[List[DireccionTipo]] = Field(None, example=[{"tipo":"personal", 
                                                                      "direccion":{"zona":"Villa Dolores","calle":"Av. 6 de Agosto","numero":"123"}}], 
                                                      title="Direccion", description="Direccion de la persona")
    telefono : Optional[Dict[str, str]] = Field(None, example={"tipo":"personal", "numero":"7777777"}, 
                                            title="Telefono", description="Numero de telefono de la persona")
    correo : Optional[Dict[str,str]] = Field(None, example={"tipo":"personal", "correo":"mendoza@gmail.com"},
                                          title="Correo", description="Correo electronico de la persona")
    
    class Config:
        from_atributes = True
        
class PersonaCreate(PersonaBase):
    pass

class PersonaLista(BaseModel):
    id_persona : UUID4 = Field(..., example="123e4567-e89b-12d3-a456-426614174000", title="Id Persona", description="Identificador unico de la persona")
    tipo : str = Field(..., example="E", title="Tipo de persona", description="Tipo de persona: 'E' = Empleado, 'P' = Paciente")
    ci : Optional[str] = Field(None, example="548732", title="Carnet de Identidad", description="Numero de carnet de identidad")
    paterno : Optional[str] = Field(None, example="Fernández", title="Apellido Paterno", description="Apellido paterno de la persona")
    materno : Optional[str] = Field(None, example="Pérez", title="Apellido Materno", description="Apellido materno de la persona")
    nombres : str = Field(..., example="Juan Antonio", title="Nombres", description="Nombres de la persona")
    fecha_nacimiento : date = Field(..., example="1990-01-01", title="Fecha de Nacimiento", description="Fecha de nacimiento de la persona")
    sexo : str = Field(..., example="M", title="Sexo", description="Sexo de la persona: 'M' = Masculino, 'F' = Femenino")
    
class RespuestaPaginada(BaseModel):
    total: int
    pagina: int
    tamanio: int
    items: List[PersonaLista]