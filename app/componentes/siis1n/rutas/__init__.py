from fastapi import APIRouter
from . import persona
router = APIRouter()

router.include_router(persona.router)