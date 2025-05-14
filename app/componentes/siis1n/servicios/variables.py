from .base import ServicioBase
from app.componentes.siis1n.modelos.variables import Variables


class ServicioVariables(ServicioBase):
    def __init__(self):
        super().__init__(Variables, 'id_variable')
