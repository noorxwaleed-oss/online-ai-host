"""
Audio Production Agent — main text-to-speech function.

Supports three providers:
  - gTTS: free, Arabic (Fusha) and English
  - Munsit: Arabic dialects (Saudi, Hijazi, Kuwaiti)
  - ElevenLabs: high-quality English voices

Auto-detection:
  - Language detected from text (Arabic chars ratio)
  - Provider selected based on language + available API keys
  - Falls back to gTTS if paid providers fail
"""

import os
import tempfile
import httpx
from typing import Dict, Any
from gtts import gTTS

from config import ELEVENLABS_KEYS, MUNSIT_KEYS
from llms import (
    get_elevenlabs_key, rotate_elevenlabs_key,
    get_munsit_key, rotate_munsit_key,
)
from prompts import (
    ENGLISH_VOICES, STYLES, MODEL_ID,
    DIALECT_VOICE_IDS,
)
from utils import upload_to_cloudinary


async def text_to_speech(
    text: str,
    provider: str = "auto",
    language: str = "auto",
    dialect: str = "fusha",
    gender: str = "male",
    style: str = "professional",
    speed: float = 1.0,
) -> Dict[str, Any]:

    if not text or not text.strip():
        return {'success': False, 'error': 'Text cannot be empty'}

    # Auto-detect language
    if language == "auto":
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        final_language = 'ar' if arabic_chars > len(text) * 0.3 else 'en'
    else:
        final_language = language

    # Auto-select provider
    final_provider = provider
    if final_provider == "auto":
        if final_language == 'ar':
            if dialect in ['saudi', 'hijazi'] and MUNSIT_KEYS:
                final_provider = 'munsit'
            else:
                final_provider = 'gtts'
        else:
            if ELEVENLABS_KEYS:
                final_provider = 'elevenlabs'
            else:
                final_provider = 'gtts'

    print(f"\n{'='*50}")
    print(f"Generating speech...")
    print(f"   Text: {text[:60]}...")
    print(f"   Language: {final_language} | Provider: {final_provider}")
    print(f"   Dialect: {dialect} | Gender: {gender} | Style: {style} | Speed: {speed}")
    print(f"{'='*50}")

    # ========== gTTS ==========
    if final_provider == 'gtts':
        print("Using gTTS")
        lang_code = 'ar' if final_language == 'ar' else 'en'
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tmp_path = tmp.name
        tts = gTTS(text=text, lang=lang_code, slow=(speed < 0.8))
        tts.save(tmp_path)
        with open(tmp_path, 'rb') as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)

        upload_result = upload_to_cloudinary(audio_bytes, '.mp3')
        if upload_result['success']:
            return {
                'success': True,
                'audio_url': upload_result['url'],
                'duration': upload_result['duration'],
                'provider': 'gtts',
                'voice': f"{'Arabic (Fusha)' if final_language=='ar' else 'English'} (gTTS)",
                'language': final_language,
            }
        else:
            return {'success': False, 'error': upload_result.get('error')}

    # ========== Munsit (Arabic dialects) ==========
    elif final_provider == 'munsit':
        voice_id_to_use = DIALECT_VOICE_IDS.get(dialect, {}).get(gender)
        if not voice_id_to_use:
            print(f"No Munsit voice for {dialect}/{gender}, falling back to gTTS")
            return await text_to_speech(text, provider='gtts', language=final_language,
                                        dialect=dialect, gender=gender, style=style, speed=speed)

        for attempt in range(len(MUNSIT_KEYS)):
            api_key = get_munsit_key()
            if not api_key:
                break

            try:
                print(f"Trying Munsit key {attempt+1}/{len(MUNSIT_KEYS)}")
                print(f"   Voice ID: {voice_id_to_use}")

                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.munsit.com/api/v1/text-to-speech/faseeh-v1-preview",
                        headers={"x-api-key": api_key, "Content-Type": "application/json"},
                        json={"text": text, "voice_id": voice_id_to_use, "speed": speed},
                    )

                    print(f"   Response Status: {response.status_code}")

                    if response.status_code == 200:
                        audio_bytes = response.content

                        if len(audio_bytes) < 1000:
                            print(f"Audio too small ({len(audio_bytes)} bytes), trying next key")
                            rotate_munsit_key()
                            continue

                        print(f"   Audio size: {len(audio_bytes)} bytes")

                        upload_result = upload_to_cloudinary(audio_bytes, '.mp3')
                        if upload_result['success']:
                            print(f"Munsit success with key {attempt+1}")
                            return {
                                'success': True,
                                'audio_url': upload_result['url'],
                                'duration': upload_result['duration'],
                                'provider': 'munsit',
                                'voice': f"{dialect.capitalize()} ({gender}) - {voice_id_to_use}",
                                'language': final_language,
                            }
                        else:
                            print(f"Upload failed: {upload_result.get('error')}")
                            rotate_munsit_key()
                    else:
                        try:
                            error_detail = response.text[:200]
                            print(f"Munsit key {attempt+1} failed (HTTP {response.status_code})")
                            print(f"   Error: {error_detail}")
                        except:
                            print(f"Munsit key {attempt+1} failed (HTTP {response.status_code})")
                        rotate_munsit_key()

            except httpx.TimeoutException:
                print(f"Munsit key {attempt+1} timeout")
                rotate_munsit_key()
            except Exception as e:
                print(f"Munsit key {attempt+1} error: {type(e).__name__}: {e}")
                rotate_munsit_key()

        print(f"All Munsit keys failed, falling back to gTTS")
        return await text_to_speech(text, provider='gtts', language=final_language,
                                    dialect=dialect, gender=gender, style=style, speed=speed)

    # ========== ElevenLabs ==========
    elif final_provider == 'elevenlabs':
        from elevenlabs.client import ElevenLabs

        selected_voice = None
        for v in ENGLISH_VOICES.values():
            if v['gender'] == gender and v['style'] == style:
                selected_voice = v
                break
        if not selected_voice:
            for v in ENGLISH_VOICES.values():
                if v['gender'] == gender:
                    selected_voice = v
                    break
        if not selected_voice:
            selected_voice = ENGLISH_VOICES['adam']

        style_settings = STYLES.get(style, STYLES["professional"])

        for attempt in range(len(ELEVENLABS_KEYS)):
            api_key = get_elevenlabs_key()
            if not api_key:
                break

            try:
                print(f"Trying ElevenLabs key {attempt+1}/{len(ELEVENLABS_KEYS)}: {selected_voice['name']}")

                client = ElevenLabs(api_key=api_key)
                audio_generator = client.text_to_speech.convert(
                    text=text,
                    voice_id=selected_voice['id'],
                    model_id=MODEL_ID,
                    output_format="mp3_44100_128",
                    voice_settings={
                        "stability": style_settings["stability"],
                        "similarity_boost": style_settings["similarity_boost"],
                    },
                )
                audio_bytes = b"".join(chunk for chunk in audio_generator)

                if len(audio_bytes) < 1000:
                    print(f"Audio too small ({len(audio_bytes)} bytes), trying next key")
                    rotate_elevenlabs_key()
                    continue

                upload_result = upload_to_cloudinary(audio_bytes, '.mp3')

                if upload_result['success']:
                    print(f"ElevenLabs success with key {attempt+1}")
                    return {
                        'success': True,
                        'audio_url': upload_result['url'],
                        'duration': upload_result['duration'],
                        'provider': 'elevenlabs',
                        'voice': selected_voice['name'],
                        'language': final_language,
                    }
                else:
                    print(f"ElevenLabs key {attempt+1} upload failed")
                    rotate_elevenlabs_key()

            except Exception as e:
                print(f"ElevenLabs key {attempt+1} error: {e}")
                rotate_elevenlabs_key()

        print(f"All ElevenLabs keys failed, falling back to gTTS")
        return await text_to_speech(text, provider='gtts', language=final_language,
                                    dialect=dialect, gender=gender, style=style, speed=speed)

    return {'success': False, 'error': f'Unknown provider: {final_provider}'}
