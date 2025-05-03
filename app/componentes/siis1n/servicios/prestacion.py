from .base import ServicioBase
from app.componentes.siis1n.modelos.prestacion import Prestacion


class ServicioPrestacion(ServicioBase):
    def __init__(self):
        super().__init__(Prestacion, 'id_prestacion')
