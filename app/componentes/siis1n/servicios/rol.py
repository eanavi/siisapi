from .base import ServicioBase
from ..modelos.rol import Rol


class ServicioRol(ServicioBase):
    def __init__(self):
        super().__init__(Rol, 'id_rol')
