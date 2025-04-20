from fastapi import APIRouter
from . import persona
from . import empleado
from . import centro
from . import rol
from . import auth
from . import paciente
from . import grupo
from . import lista

router = APIRouter()

router.include_router(persona.router)
router.include_router(empleado.router)
router.include_router(centro.router)
router.include_router(rol.router)
router.include_router(auth.router)
router.include_router(paciente.router)
router.include_router(grupo.router)
router.include_router(lista.router)
