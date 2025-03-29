from .base import ServicioBase
from ..modelos.usuario import Usuario


class ServicioUsuario(ServicioBase):
    def __init__(self):
        super().__init__(Usuario, 'id_usuario')
