from fastapi import APIRouter
from .parcels import router as parcels_router
from .map import router as map_router

api_router = APIRouter()
api_router.include_router(parcels_router)
api_router.include_router(map_router)
