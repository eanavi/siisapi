from sqlalchemy.types import UserDefinedType
from sqlalchemy.dialects.postgresql import TEXT
from .edad import Edad


class TipoEdad(UserDefinedType):
    def get_col_spec(self, **kwargs):
        return "edad"  # Especifica el tipo de columna en PostgreSQL

    def bind_processor(self, dialect):
        def process(value):
            # Convierte el valor de Python a un formato compatible con PostgreSQL
            if value is None:
                return None
            return f"({value.anio},{value.mes},{value.dia})"
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            # Convierte el valor de PostgreSQL a un objeto Python
            if value is None:
                return None
            anio, mes, dia = map(int, value.strip("()").split(","))
            return Edad(anio=anio, mes=mes, dia=dia)
        return process
