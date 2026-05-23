"""
Data schemas for the Publishing Agent — v3.0 (RSS-based).

The Publishing Agent generates and updates an RSS feed XML file
hosted on Cloudinary. Podcast platforms (Spotify, Anghami, Apple Podcasts,
YouTube Music) auto-pull new episodes from this feed.

Flow:
  1. First publish: generates RSS feed → uploads to Cloudinary → returns feed URL
  2. Subsequent publishes: fetches existing feed → adds new episode → re-uploads
  3. User submits the feed URL once to each platform dashboard
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ---------- INPUT MODELS ----------

class EpisodeAssets(BaseModel):
    """A single episode ready for publishing."""
    script_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=4000)
    audio_url: str = Field(
        ...,
        description="Cloudinary URL of the MP3 produced by the Audio Production Agent"
    )
    cover_image_url: str = Field(
        ...,
        description="Cloudinary URL of the episode cover art"
    )
    duration_seconds: Optional[int] = Field(None, ge=1)
    tags: list[str] = Field(default_factory=list, max_length=10)


class PodcastInfo(BaseModel):
    """Podcast-level metadata (set once, reused for every episode)."""
    podcast_title: str = Field(..., min_length=1, max_length=200)
    podcast_description: str = Field(..., min_length=10, max_length=4000)
    author: str = Field(..., min_length=1)
    language: str = Field(default="ar", description="ISO code, e.g., 'ar', 'en'")
    category: str = Field(default="Technology", description="iTunes podcast category")
    cover_image_url: str = Field(
        ...,
        description="Cloudinary URL of the podcast cover (square, min 1400x1400)"
    )


class PublishingInput(BaseModel):
    """Full input the Publishing Agent accepts from the pipeline."""
    episode: EpisodeAssets
    podcast: PodcastInfo
    existing_feed_url: Optional[str] = Field(
        None,
        description="Cloudinary URL of existing RSS feed. None = first episode, create new feed."
    )


# ---------- OUTPUT MODELS ----------

class PublishingOutput(BaseModel):
    """Full output the Publishing Agent returns to the pipeline."""
    script_id: str
    success: bool
    feed_url: str = Field(
        ...,
        description="Cloudinary URL of the RSS feed. User submits this once to each platform."
    )
    episode_count: int = Field(..., ge=1)
    episode_title: str
    error_message: Optional[str] = None
    timestamp: datetime
