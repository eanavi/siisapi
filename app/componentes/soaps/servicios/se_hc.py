from .base import ServBase
from app.componentes.soaps.modelos.se_hc import Se_hc


class ServicioSe_Hc(ServBase):
    def __init__(self):
        super().__init__(Se_hc, "HCL_CODIGO")
