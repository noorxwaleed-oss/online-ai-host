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
  - Munsit: Arabic dialect voices (Saudi, Hijazi, Kuwaiti, Egyptian), paid API
"""

import os
import tempfile
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



