from fastapi import APIRouter
from . import se_hc

router = APIRouter(prefix="/soaps")

router.include_router(se_hc.router)
