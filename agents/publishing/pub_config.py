"""Centralized configuration for the Publishing Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()

# Platform API Keys (for future real adapters)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
ANGHAMI_API_KEY = os.getenv("ANGHAMI_API_KEY", "")
YOUTUBE_MUSIC_API_KEY = os.getenv("YOUTUBE_MUSIC_API_KEY", "")
APPLE_PODCASTS_API_KEY = os.getenv("APPLE_PODCASTS_API_KEY", "")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
