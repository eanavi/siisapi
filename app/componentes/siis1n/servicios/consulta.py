from .base import ServicioBase
from ..modelos.consulta import Consulta

class ServicioConsulta(ServicioBase):
    def __init__(self):
        super().__init__(Consulta, 'id_consulta')