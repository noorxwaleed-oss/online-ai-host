"""
Mock adapters for v1.0.

Each adapter simulates publishing without making real API calls. They
generate fake URLs, write to a local audit log, and return results that
look real to the Orchestrator.

To swap in a real implementation later, replace one adapter file at a time.
The base interface and agent code don't change.
"""

import json
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from models import (
    PublishableAssets,
    PlatformResult,
    PublishStatus,
    Platform,
)


# ---------- MOCK STATE ----------
# In real code this would be a database. For mocks, a dict + a JSON file.

MOCK_CONNECTIONS: dict[str, set[Platform]] = {
    # Pretend user "demo_user" has linked these platforms.
    # The Orchestrator would normally populate this from the credential DB.
    "demo_user": {Platform.SPOTIFY, Platform.ANGHAMI, Platform.YOUTUBE_MUSIC, Platform.APPLE_PODCASTS},
}

AUDIT_LOG_PATH = Path(__file__).parent / "audit_log.jsonl"


def _write_audit(record: dict):
    """Append a record to the audit log (one JSON object per line)."""
    AUDIT_LOG_PATH.parent.mkdir(exist_ok=True, parents=True)
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def _simulate_network_latency():
    """Mock adapters sleep briefly so demos feel realistic."""
    time.sleep(random.uniform(0.2, 0.6))


def _check_assets(assets: PublishableAssets) -> str | None:
    """Validate that the asset paths exist. Returns error message or None."""
    audio = Path(assets.audio_file_path)
    cover = Path(assets.cover_image_path)
    if not audio.exists():
        return f"Audio file not found: {assets.audio_file_path}"
    if not cover.exists():
        return f"Cover image not found: {assets.cover_image_path}"
    return None


# ====================================================================
# SPOTIFY — Podcast / music distribution
# ====================================================================

class SpotifyAdapter:
    platform = Platform.SPOTIFY

    def is_connected(self, user_id: str) -> bool:
        return Platform.SPOTIFY in MOCK_CONNECTIONS.get(user_id, set())

    def publish(self, assets: PublishableAssets, user_id: str) -> PlatformResult:
        start = time.time()
        _simulate_network_latency()

        err = _check_assets(assets)
        if err:
            return PlatformResult(
                platform=self.platform,
                status=PublishStatus.FAILED,
                error_message=err,
                latency_ms=int((time.time() - start) * 1000),
            )

        episode_id = f"spot_{uuid.uuid4().hex[:10]}"
        url = f"https://mock-spotify.com/episode/{episode_id}"

        _write_audit({
            "platform": self.platform.value,
            "user_id": user_id,
            "script_id": assets.script_id,
            "title": assets.title,
            "audio_path": assets.audio_file_path,
            "cover_path": assets.cover_image_path,
            "platform_post_id": episode_id,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return PlatformResult(
            platform=self.platform,
            status=PublishStatus.SUCCESS,
            published_url=url,
            platform_post_id=episode_id,
            published_at=datetime.now(timezone.utc),
            latency_ms=int((time.time() - start) * 1000),
        )


# ====================================================================
# ANGHAMI — Middle Eastern music streaming platform
# ====================================================================

class AnghamiAdapter:
    platform = Platform.ANGHAMI

    def is_connected(self, user_id: str) -> bool:
        return Platform.ANGHAMI in MOCK_CONNECTIONS.get(user_id, set())

    def publish(self, assets: PublishableAssets, user_id: str) -> PlatformResult:
        start = time.time()
        _simulate_network_latency()

        err = _check_assets(assets)
        if err:
            return PlatformResult(
                platform=self.platform,
                status=PublishStatus.FAILED,
                error_message=err,
                latency_ms=int((time.time() - start) * 1000),
            )

        track_id = f"ang_{uuid.uuid4().hex[:12]}"
        url = f"https://mock-anghami.com/track/{track_id}"

        _write_audit({
            "platform": self.platform.value,
            "user_id": user_id,
            "script_id": assets.script_id,
            "title": assets.title,
            "audio_path": assets.audio_file_path,
            "cover_path": assets.cover_image_path,
            "platform_post_id": track_id,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return PlatformResult(
            platform=self.platform,
            status=PublishStatus.SUCCESS,
            published_url=url,
            platform_post_id=track_id,
            published_at=datetime.now(timezone.utc),
            latency_ms=int((time.time() - start) * 1000),
        )


# ====================================================================
# YOUTUBE MUSIC
# ====================================================================

class YouTubeMusicAdapter:
    platform = Platform.YOUTUBE_MUSIC

    def is_connected(self, user_id: str) -> bool:
        return Platform.YOUTUBE_MUSIC in MOCK_CONNECTIONS.get(user_id, set())

    def publish(self, assets: PublishableAssets, user_id: str) -> PlatformResult:
        start = time.time()
        _simulate_network_latency()

        err = _check_assets(assets)
        if err:
            return PlatformResult(
                platform=self.platform,
                status=PublishStatus.FAILED,
                error_message=err,
                latency_ms=int((time.time() - start) * 1000),
            )

        video_id = f"ytm_{uuid.uuid4().hex[:11]}"
        url = f"https://mock-youtube-music.com/watch?v={video_id}"

        _write_audit({
            "platform": self.platform.value,
            "user_id": user_id,
            "script_id": assets.script_id,
            "title": assets.title,
            "audio_path": assets.audio_file_path,
            "cover_path": assets.cover_image_path,
            "platform_post_id": video_id,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return PlatformResult(
            platform=self.platform,
            status=PublishStatus.SUCCESS,
            published_url=url,
            platform_post_id=video_id,
            published_at=datetime.now(timezone.utc),
            latency_ms=int((time.time() - start) * 1000),
        )


# ====================================================================
# APPLE PODCASTS
# ====================================================================

class ApplePodcastsAdapter:
    platform = Platform.APPLE_PODCASTS

    def is_connected(self, user_id: str) -> bool:
        return Platform.APPLE_PODCASTS in MOCK_CONNECTIONS.get(user_id, set())

    def publish(self, assets: PublishableAssets, user_id: str) -> PlatformResult:
        start = time.time()
        _simulate_network_latency()

        err = _check_assets(assets)
        if err:
            return PlatformResult(
                platform=self.platform,
                status=PublishStatus.FAILED,
                error_message=err,
                latency_ms=int((time.time() - start) * 1000),
            )

        episode_id = f"ap_{uuid.uuid4().hex[:10]}"
        url = f"https://mock-apple-podcasts.com/episode/{episode_id}"

        _write_audit({
            "platform": self.platform.value,
            "user_id": user_id,
            "script_id": assets.script_id,
            "title": assets.title,
            "audio_path": assets.audio_file_path,
            "cover_path": assets.cover_image_path,
            "platform_post_id": episode_id,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return PlatformResult(
            platform=self.platform,
            status=PublishStatus.SUCCESS,
            published_url=url,
            platform_post_id=episode_id,
            published_at=datetime.now(timezone.utc),
            latency_ms=int((time.time() - start) * 1000),
        )


# ---------- REGISTRY ----------
# Maps platform enum → adapter instance. The agent uses this to dispatch.

ALL_ADAPTERS: dict[Platform, "PublishingAdapter"] = {
    Platform.SPOTIFY: SpotifyAdapter(),
    Platform.ANGHAMI: AnghamiAdapter(),
    Platform.YOUTUBE_MUSIC: YouTubeMusicAdapter(),
    Platform.APPLE_PODCASTS: ApplePodcastsAdapter(),
}