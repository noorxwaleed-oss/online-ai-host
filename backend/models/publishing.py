from pydantic import BaseModel
from typing import Optional

class EpisodeAssets(BaseModel):
    script_id: str
    title: str
    description: str
    audio_url: str
    cover_image_url: str
    duration_seconds: int

class PodcastInfo(BaseModel):
    podcast_title: str
    podcast_description: str
    author: str
    language: str
    category: str
    cover_image_url: str

class PublishingInput(BaseModel):
    episode: EpisodeAssets
    podcast: PodcastInfo
    existing_feed_url: Optional[str] = None
