from pydantic import BaseModel, model_validator
from app.componentes.siis1n.modelos.edad import Edad
from app.utiles.varios import validar_fecha_de_edad


class EdadPydantic(BaseModel):
    anio: int
    mes: int
    dia: int

    @model_validator(mode="before")
    @classmethod
    def validar_edad(cls, values):
        if isinstance(values, Edad):
            anio = values.anio
            mes = values.mes
            dia = values.dia
        else:
            anio = values.get("anio")
            mes = values.get("mes")
            dia = values.get("dia")

        validar_fecha_de_edad(anio, mes, dia)

        return values

    def to_internal(self) -> Edad:
        """Convierte la instancia de Pydantic a la clase interna `Edad`."""
        return Edad(self.anio, self.mes, self.dia)

    @classmethod
    def from_internal(cls, edad: Edad) -> "EdadPydantic":
        """Crea una instancia de `EdadPydantic` a partir de una instancia de `Edad`."""
        return cls(anio=edad.anio, mes=edad.mes, dia=edad.dia)
