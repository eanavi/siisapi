from fastapi import APIRouter
from . import persona
from . import empleado
router = APIRouter()

router.include_router(persona.router)
router.include_router(empleado.router)
