from pydantic import BaseModel
from typing import Optional, List

class PodcastCreate(BaseModel):
    host_name: str
    host_gender: str
    guest_name: str
    guest_gender: str
    podcast_name: str
    language: str
    content: str
    voice_id_host: str
    voice_id_guest: str
    host_style: str
    guest_style: str
    user_id: str

class PodcastResponse(BaseModel):
    message: str
    audio_url: Optional[str] = None
    duration: float = 0.0
    error: Optional[str] = None
