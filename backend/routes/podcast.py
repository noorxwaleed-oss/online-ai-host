from fastapi import APIRouter, Depends
from backend.schemas.podcast import PodcastCreate, PodcastResponse
from backend.services.podcast_service import process_podcast_pipeline

router = APIRouter()

@router.post("/", response_model=PodcastResponse)
async def create_podcast(data: PodcastCreate):
    return await process_podcast_pipeline(data)
