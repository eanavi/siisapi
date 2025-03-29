from .base import ServicioBase
from ..modelos.centro import Centro


class ServicioCentro(ServicioBase):
    def __init__(self):
        super().__init__(Centro, 'id_centro')
