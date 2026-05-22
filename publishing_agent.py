"""
Publishing Agent — v3.0 (RSS-based).

Instead of calling platform APIs, generates an RSS feed XML file
and uploads it to Cloudinary. Podcast platforms auto-pull from this feed.

Flow:
  1. First episode: create_new_feed() → upload to Cloudinary
  2. New episodes: fetch existing feed → add_episode_to_existing_feed() → re-upload
"""

import json
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
import cloudinary
import cloudinary.uploader
from pub_models import PublishingInput, PublishingOutput
from rss_builder import create_new_feed, add_episode_to_existing_feed, count_episodes
from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET


# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

AUDIT_LOG_PATH = Path(__file__).parent / "audit_log.jsonl"


def _write_audit(record: dict):
    """Append a record to the audit log."""
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def _upload_feed_to_cloudinary(xml_string: str, user_id: str = "default") -> dict:
    """Upload the RSS XML to Cloudinary, overwriting if exists."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False, encoding="utf-8") as f:
        f.write(xml_string)
        temp_path = f.name

    try:
        result = cloudinary.uploader.upload(
            temp_path,
            resource_type="raw",
            folder=f"users/{user_id}/podcast",
            public_id="feed",
            overwrite=True,
            invalidate=True,
        )
        return {"success": True, "url": result["secure_url"]}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        os.unlink(temp_path)


class PublishingAgent:
    """Generates and updates RSS podcast feeds on Cloudinary."""

    def publish(self, inp: PublishingInput, user_id: str = "default") -> PublishingOutput:
        """Publish a new episode to the RSS feed."""
        try:
            if inp.existing_feed_url:
                # Fetch existing feed, add episode
                response = requests.get(inp.existing_feed_url)
                response.raise_for_status()
                existing_xml = response.text
                updated_xml = add_episode_to_existing_feed(existing_xml, inp.episode)
            else:
                # First episode — create new feed
                updated_xml = create_new_feed(inp.podcast, inp.episode)

            # Upload to Cloudinary
            upload_result = _upload_feed_to_cloudinary(updated_xml, user_id)

            if not upload_result["success"]:
                return PublishingOutput(
                    script_id=inp.episode.script_id,
                    success=False,
                    feed_url="",
                    episode_count=0,
                    episode_title=inp.episode.title,
                    error_message=f"Cloudinary upload failed: {upload_result['error']}",
                    timestamp=datetime.now(timezone.utc),
                )

            episode_count = count_episodes(updated_xml)

            _write_audit({
                "action": "episode_published",
                "script_id": inp.episode.script_id,
                "episode_title": inp.episode.title,
                "audio_url": inp.episode.audio_url,
                "feed_url": upload_result["url"],
                "episode_count": episode_count,
                "is_new_feed": inp.existing_feed_url is None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            return PublishingOutput(
                script_id=inp.episode.script_id,
                success=True,
                feed_url=upload_result["url"],
                episode_count=episode_count,
                episode_title=inp.episode.title,
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as e:
            return PublishingOutput(
                script_id=inp.episode.script_id,
                success=False,
                feed_url=inp.existing_feed_url or "",
                episode_count=0,
                episode_title=inp.episode.title,
                error_message=f"{type(e).__name__}: {e}",
                timestamp=datetime.now(timezone.utc),
            )
