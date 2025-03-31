from fastapi import APIRouter
from . import persona
from . import empleado
from . import centro
from . import rol

router = APIRouter()

router.include_router(persona.router)
router.include_router(empleado.router)
router.include_router(centro.router)
router.include_router(rol.router)
