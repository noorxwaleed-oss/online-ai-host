from fastapi import APIRouter
from backend.routes import podcast

api_router = APIRouter()
api_router.include_router(podcast.router, prefix="/podcast", tags=["podcast"])
