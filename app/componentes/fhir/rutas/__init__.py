from fastapi import APIRouter

from . import paciente

router = APIRouter(prefix="/fhir")

router.include_router(paciente.router)