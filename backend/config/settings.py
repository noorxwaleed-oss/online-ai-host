import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Online AI-host"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # LLM Settings
    TEXTGENERATION_MODEL: str = os.getenv("TEXTGENERATION_MODEL", "gpt-3.5-turbo")
    TEXTGENERATION_HF_TOKEN: str = os.getenv("TEXTGENERATION_HF_token", "")
    TEXTGENERATION_BASE_URL: str = os.getenv("TEXTGENERATION_BASE_URL", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    HF_TOKEN_COVERART: str = os.getenv("HF_TOKEN_coverArt", "")

    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    # ElevenLabs Keys
    @property
    def ELEVENLABS_KEYS(self) -> list[str]:
        keys = []
        for i in range(1, 10):
            key = os.getenv(f"ELEVENLABS_API_KEY{i}")
            if key:
                keys.append(key)
        return keys

    # Munsit Keys
    @property
    def MUNSIT_KEYS(self) -> list[str]:
        keys = []
        for i in range(1, 10):
            key = os.getenv(f"MUNSIT_API_KEY{i}")
            if key:
                keys.append(key)
        return keys

    # Image Generation
    IMAGE_MODEL: str = "Tongyi-MAI/Z-Image-Turbo"
    ASPECT_RATIOS: dict = {
        "1:1": (768, 768),
        "16:9": (1024, 576),
        "4:5": (768, 960),
        "2:3": (768, 1152)
    }

settings = Settings()
