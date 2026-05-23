import json
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path
import requests
import cloudinary.uploader
from backend.models.publishing import PublishingInput
from backend.schemas.podcast import PodcastResponse # Using schemas for consistency
from backend.agents.rss_builder import create_new_feed, add_episode_to_existing_feed, count_episodes
from backend.config.settings import settings
from backend.cloudinary.config import cloudinary_config
from pydantic import BaseModel

class PublishingOutput(BaseModel):
    script_id: str
    success: bool
    feed_url: str
    episode_count: int
    episode_title: str
    error_message: str = ""
    timestamp: datetime

def _upload_feed_to_cloudinary(xml_string: str, user_id: str = "default") -> dict:
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
        if os.path.exists(temp_path): os.unlink(temp_path)

class PublishingAgent:
    def publish(self, inp: PublishingInput, user_id: str = "default") -> PublishingOutput:
        try:
            if inp.existing_feed_url:
                response = requests.get(inp.existing_feed_url)
                response.raise_for_status()
                updated_xml = add_episode_to_existing_feed(response.text, inp.episode)
            else:
                updated_xml = create_new_feed(inp.podcast, inp.episode)

            upload_result = _upload_feed_to_cloudinary(updated_xml, user_id)
            if not upload_result["success"]:
                return PublishingOutput(script_id=inp.episode.script_id, success=False, feed_url="", episode_count=0, episode_title=inp.episode.title, error_message=upload_result['error'], timestamp=datetime.now(timezone.utc))

            episode_count = count_episodes(updated_xml)
            return PublishingOutput(script_id=inp.episode.script_id, success=True, feed_url=upload_result["url"], episode_count=episode_count, episode_title=inp.episode.title, timestamp=datetime.now(timezone.utc))
        except Exception as e:
            return PublishingOutput(script_id=inp.episode.script_id, success=False, feed_url=inp.existing_feed_url or "", episode_count=0, episode_title=inp.episode.title, error_message=str(e), timestamp=datetime.now(timezone.utc))
