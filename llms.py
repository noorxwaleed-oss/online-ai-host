from langchain_openai import ChatOpenAI
from config import textGeneration_model, textGeneration_HF_token , textGeneration_base_url

generateTextLlm = ChatOpenAI(model=textGeneration_model
                 , api_key=textGeneration_HF_token
                 ,base_url=textGeneration_base_url
                 ,temperature=0.2)



# ========= ElevenLabs Keys Management ==========

"""
Voice provider clients for the Audio Production Agent.

Providers:
  - gTTS: free, supports Arabic (Fusha) and English
  - ElevenLabs: high-quality English voices, paid API
  - Munsit: Arabic dialect voices (Saudi, Hijazi, Kuwaiti), paid API
"""

import os
import tempfile
import time
import httpx
from typing import Dict, Any
from gtts import gTTS

from config import ELEVENLABS_KEYS, MUNSIT_KEYS


# ========== ElevenLabs Key Rotation ==========

ELEVENLABS_CURRENT_INDEX = 0


def get_elevenlabs_key():
    if not ELEVENLABS_KEYS:
        return None
    return ELEVENLABS_KEYS[ELEVENLABS_CURRENT_INDEX]


def rotate_elevenlabs_key():
    global ELEVENLABS_CURRENT_INDEX
    if not ELEVENLABS_KEYS:
        return None
    ELEVENLABS_CURRENT_INDEX = (ELEVENLABS_CURRENT_INDEX + 1) % len(ELEVENLABS_KEYS)
    return get_elevenlabs_key()


# ========== Munsit Key Rotation ==========

MUNSIT_CURRENT_INDEX = 0


def get_munsit_key():
    if not MUNSIT_KEYS:
        return None
    return MUNSIT_KEYS[MUNSIT_CURRENT_INDEX]


def rotate_munsit_key():
    global MUNSIT_CURRENT_INDEX
    if not MUNSIT_KEYS:
        return None
    MUNSIT_CURRENT_INDEX = (MUNSIT_CURRENT_INDEX + 1) % len(MUNSIT_KEYS)
    return get_munsit_key()


# ========== gTTS ==========

def generate_gtts(text: str, language: str, speed: float = 1.0) -> bytes:
    """Generating audio using gTTS (Fusha Arabic or English)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
        tmp_path = tmp.name

    lang_code = 'ar' if language == 'ar' else 'en'
    tts = gTTS(text=text, lang=lang_code, slow=(speed < 0.8))
    tts.save(tmp_path)

    with open(tmp_path, 'rb') as f:
        audio_bytes = f.read()

    os.unlink(tmp_path)
    return audio_bytes







import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"




# =======================================================


"""
Concrete LLM client implementations.

We provide a Groq client (recommended for development — fast, free tier).
Add other clients (Together, OpenAI, local) by following the same pattern.

To use Groq:
    pip install groq
    export GROQ_API_KEY=your_key_here
"""

import os


class GroqLLMClient:
    """
    Groq client for Llama 3.3 70B.
    Fast inference, generous free tier, ideal for development.
    """

    model_name = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        try:
            from groq import Groq
        except ImportError:
            raise ImportError(
                "groq package not installed. Run: pip install groq"
            )

        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it as an environment variable or pass api_key=..."
            )

        self.client = Groq(api_key=api_key)
        if model:
            self.model_name = model

    def complete(self, system_prompt: str, user_prompt: str) -> tuple[str, int]:
        """Returns (response_text, total_tokens_used)."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,  # Low temp = consistent evaluation, not creative
            max_tokens=1500,  # Critic output is structured + bounded
            response_format={"type": "json_object"},  # Forces valid JSON
        )
        text = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        return text, tokens


class MockLLMClient:
    """
    Mock client for unit tests.
    Returns canned responses without hitting any API.
    Lets you test the agent's logic without spending tokens.
    """

    model_name = "mock-llm-v1"

    def __init__(self, canned_response: str):
        self.canned_response = canned_response
        self.call_count = 0

    def complete(self, system_prompt: str, user_prompt: str) -> tuple[str, int]:
        self.call_count += 1
        return self.canned_response, 0
