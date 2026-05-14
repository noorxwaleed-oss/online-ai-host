"""
Data schemas for the Publishing Agent — v1.0.

The Publishing Agent accepts approved assets (script, audio, cover) plus a
list of platforms to publish to, and returns per-platform results.

Design notes:
- All adapters in this v1.0 are MOCKED. No real OAuth, no real API calls.
- Real implementations would replace mock adapters one-for-one without
  changing this contract.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ---------- PLATFORMS ----------

class Platform(str, Enum):
    """The platforms our Publishing Agent supports."""
    BUZZSPROUT = "buzzsprout"     # Podcast distributor (Spotify/Apple/Google)
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"


# ---------- INPUT MODELS ----------

class PublishableAssets(BaseModel):
    """The approved content bundle ready for publishing."""
    script_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    audio_file_path: str = Field(
        ...,
        description="Path to the MP3 file produced by the Audio Production Agent"
    )
    cover_image_path: str = Field(
        ...,
        description="Path to the JPG/PNG cover art produced by the Cover Design Agent"
    )
    transcript: Optional[str] = Field(
        None,
        description="Optional full-text transcript (some platforms accept this)"
    )
    tags: list[str] = Field(default_factory=list, max_length=10)
    duration_seconds: Optional[int] = Field(None, ge=1)


class UserContext(BaseModel):
    """Identifies the user and their connected accounts.

    For v1.0 (mocked): user_id is just a string. No real credentials.
    For production: this would reference a credential vault keyed by user_id.
    """
    user_id: str
    connected_platforms: list[Platform] = Field(
        default_factory=list,
        description="Platforms the user has linked (would be from credential DB)"
    )


class PublishingInput(BaseModel):
    """Full input the Publishing Agent accepts from the Orchestrator."""
    assets: PublishableAssets
    user: UserContext
    target_platforms: list[Platform] = Field(
        ...,
        min_length=1,
        description="Which platforms to publish to in this request"
    )

    @field_validator("target_platforms")
    @classmethod
    def validate_no_duplicates(cls, v: list[Platform]) -> list[Platform]:
        if len(v) != len(set(v)):
            raise ValueError("target_platforms must not contain duplicates")
        return v


# ---------- OUTPUT MODELS ----------

class PublishStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED_NOT_CONNECTED = "SKIPPED_NOT_CONNECTED"  # user hasn't linked the platform


class PlatformResult(BaseModel):
    """Per-platform publishing result."""
    platform: Platform
    status: PublishStatus
    published_url: Optional[str] = Field(
        None,
        description="Live URL of the published content (None if not SUCCESS)"
    )
    platform_post_id: Optional[str] = Field(
        None,
        description="The platform's internal ID for the published item"
    )
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None
    latency_ms: int = Field(..., ge=0)


class PublishingOutput(BaseModel):
    """Full output the Publishing Agent returns to the Orchestrator."""
    script_id: str
    overall_status: PublishStatus = Field(
        ...,
        description="SUCCESS if all targeted platforms succeeded; FAILED if any failed"
    )
    total_succeeded: int = Field(..., ge=0)
    total_failed: int = Field(..., ge=0)
    total_skipped: int = Field(..., ge=0)
    results: list[PlatformResult]
    timestamp: datetime
