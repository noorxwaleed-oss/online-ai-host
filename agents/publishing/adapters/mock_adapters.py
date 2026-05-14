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

from schemas.models import (
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
    "demo_user": {Platform.BUZZSPROUT, Platform.LINKEDIN, Platform.TWITTER, Platform.INSTAGRAM},
}

AUDIT_LOG_PATH = Path(__file__).parent.parent / "audit_log.jsonl"


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
# BUZZSPROUT — Podcast distribution (covers Spotify/Apple/Google)
# ====================================================================

class BuzzsproutAdapter:
    platform = Platform.BUZZSPROUT

    def is_connected(self, user_id: str) -> bool:
        return Platform.BUZZSPROUT in MOCK_CONNECTIONS.get(user_id, set())

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

        episode_id = f"bzp_{uuid.uuid4().hex[:10]}"
        url = f"https://mock-buzzsprout.com/episodes/{episode_id}"

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
# LINKEDIN
# ====================================================================

class LinkedInAdapter:
    platform = Platform.LINKEDIN

    def is_connected(self, user_id: str) -> bool:
        return Platform.LINKEDIN in MOCK_CONNECTIONS.get(user_id, set())

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

        # LinkedIn posts have title + description + cover image link
        if len(assets.description) > 1300:
            return PlatformResult(
                platform=self.platform,
                status=PublishStatus.FAILED,
                error_message="LinkedIn post body exceeds 1300 character limit",
                latency_ms=int((time.time() - start) * 1000),
            )

        post_id = f"li_{uuid.uuid4().hex[:12]}"
        url = f"https://mock-linkedin.com/posts/{post_id}"

        _write_audit({
            "platform": self.platform.value,
            "user_id": user_id,
            "script_id": assets.script_id,
            "title": assets.title,
            "platform_post_id": post_id,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return PlatformResult(
            platform=self.platform,
            status=PublishStatus.SUCCESS,
            published_url=url,
            platform_post_id=post_id,
            published_at=datetime.now(timezone.utc),
            latency_ms=int((time.time() - start) * 1000),
        )


# ====================================================================
# TWITTER / X
# ====================================================================

class TwitterAdapter:
    platform = Platform.TWITTER

    def is_connected(self, user_id: str) -> bool:
        return Platform.TWITTER in MOCK_CONNECTIONS.get(user_id, set())

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

        # Twitter has a 280-char limit. Truncate the description for the tweet.
        tweet_text = f"{assets.title}\n\n{assets.description}"
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        post_id = f"tw_{uuid.uuid4().hex[:14]}"
        url = f"https://mock-twitter.com/status/{post_id}"

        _write_audit({
            "platform": self.platform.value,
            "user_id": user_id,
            "script_id": assets.script_id,
            "tweet_text": tweet_text,
            "platform_post_id": post_id,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return PlatformResult(
            platform=self.platform,
            status=PublishStatus.SUCCESS,
            published_url=url,
            platform_post_id=post_id,
            published_at=datetime.now(timezone.utc),
            latency_ms=int((time.time() - start) * 1000),
        )


# ====================================================================
# INSTAGRAM
# ====================================================================

class InstagramAdapter:
    platform = Platform.INSTAGRAM

    def is_connected(self, user_id: str) -> bool:
        return Platform.INSTAGRAM in MOCK_CONNECTIONS.get(user_id, set())

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

        # Instagram requires a square image. Real adapter would crop/validate.
        # Mock just trusts the input.
        post_id = f"ig_{uuid.uuid4().hex[:12]}"
        url = f"https://mock-instagram.com/p/{post_id}"

        _write_audit({
            "platform": self.platform.value,
            "user_id": user_id,
            "script_id": assets.script_id,
            "title": assets.title,
            "platform_post_id": post_id,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return PlatformResult(
            platform=self.platform,
            status=PublishStatus.SUCCESS,
            published_url=url,
            platform_post_id=post_id,
            published_at=datetime.now(timezone.utc),
            latency_ms=int((time.time() - start) * 1000),
        )


# ---------- REGISTRY ----------
# Maps platform enum → adapter instance. The agent uses this to dispatch.

ALL_ADAPTERS: dict[Platform, "PublishingAdapter"] = {
    Platform.BUZZSPROUT: BuzzsproutAdapter(),
    Platform.LINKEDIN: LinkedInAdapter(),
    Platform.TWITTER: TwitterAdapter(),
    Platform.INSTAGRAM: InstagramAdapter(),
}
