"""
Audio Production Agent — main text-to-speech and podcast generation.

Supports three providers:
  - gTTS: free, Arabic (Fusha) and English
  - Munsit: Arabic dialects (default for all Arabic)
  - ElevenLabs: high-quality English voices

v2 changes from v1:
  - Munsit is now default for ALL Arabic (including fusha)
  - voice_id parameter for explicit voice override
  - generate_podcast_from_script: full pipeline from raw script to combined audio
  - Auto audio format detection on upload
"""

import os
import tempfile
import io
import httpx
import requests
from typing import Dict, Any
from gtts import gTTS
from pydub import AudioSegment

from config import ELEVENLABS_KEYS, MUNSIT_KEYS
from llms import (
    get_elevenlabs_key, rotate_elevenlabs_key,
    get_munsit_key, rotate_munsit_key,
)
from prompts import ENGLISH_VOICES, STYLES, MODEL_ID
from utils import upload_to_cloudinary, load_audio_safely, parse_script


async def text_to_speech(
    text: str,
    provider: str = "auto",
    language: str = "auto",
    dialect: str = "fusha",
    gender: str = "male",
    style: str = "professional",
    speed: float = 1.0,
    voice_id: str = None,
) -> Dict[str, Any]:

    if not text or not text.strip():
        return {'success': False, 'error': 'Text cannot be empty'}

    # Auto-detect language
    if language == "auto":
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        final_language = 'ar' if arabic_chars > len(text) * 0.3 else 'en'
    else:
        final_language = language

    # Auto-select provider — Munsit is now default for ALL Arabic
    final_provider = provider
    if final_provider == "auto":
        if final_language == 'ar':
            if MUNSIT_KEYS:
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

    # ========== Munsit (Arabic — all dialects) ==========
    elif final_provider == 'munsit':
        # Explicit voice_id override takes priority
        if voice_id:
            voice_id_to_use = voice_id
        elif dialect == 'saudi':
            voice_id_to_use = 'ar-najdi-male-2' if gender == 'male' else 'ar-najdi-female-1'
        elif dialect == 'hijazi':
            voice_id_to_use = 'ar-hijazi-female-1' if gender == 'female' else 'ar-najdi-male-2'
        elif dialect == 'kuwaiti':
            voice_id_to_use = 'ar-kuwaiti-male-1' if gender == 'male' else 'ar-najdi-female-1'
        elif dialect == 'egyptian':
            voice_id_to_use = 'ar-egyptian-male-1' if gender == 'male' else 'ar-najdi-female-1'
        else:
            # fusha or any other → pick a sensible Munsit voice by gender
            voice_id_to_use = 'ar-najdi-male-2' if gender == 'male' else 'ar-najdi-female-1'

        for attempt in range(len(MUNSIT_KEYS)):
            api_key = get_munsit_key()
            if not api_key:
                break

            try:
                print(f"Trying Munsit key {attempt+1}/{len(MUNSIT_KEYS)} | voice={voice_id_to_use}")

                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        "https://api.munsit.com/api/v1/text-to-speech/faseeh-v1-preview",
                        headers={"x-api-key": api_key, "Content-Type": "application/json"},
                        json={"text": text, "voice_id": voice_id_to_use, "speed": speed},
                    )

                    if response.status_code == 200:
                        audio_bytes = response.content
                        if len(audio_bytes) < 1000:
                            print(f"Audio too small ({len(audio_bytes)} bytes), trying next key")
                            rotate_munsit_key()
                            continue

                        upload_result = upload_to_cloudinary(audio_bytes, '.mp3')
                        if upload_result['success']:
                            print(f"Munsit success with key {attempt+1}")
                            return {
                                'success': True,
                                'audio_url': upload_result['url'],
                                'duration': upload_result['duration'],
                                'provider': 'munsit',
                                'voice': f"{voice_id_to_use} ({gender})",
                                'language': final_language,
                            }
                    else:
                        print(f"Munsit key {attempt+1} failed (HTTP {response.status_code}): {response.text[:200]}")
                        rotate_munsit_key()

            except Exception as e:
                print(f"Munsit key {attempt+1} error: {e}")
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


async def generate_podcast_from_script(
    raw_text: str,
    host_config: Dict[str, Any],
    guest_config: Dict[str, Any],
    speed: float = 1.0,
) -> Dict[str, Any]:
    """Generate a full podcast from a raw Host:/Guest: script."""

    script = parse_script(raw_text)

    if not script:
        return {'success': False, 'error': 'No valid script found. Use "Host:" and "Guest:" labels.'}

    print("=" * 60)
    print("Parsing Script")
    print(f"   Total turns detected: {len(script)}")
    print("=" * 60)

    for i, item in enumerate(script):
        print(f"   [{i+1}] {item['speaker'].upper()}: {item['text'][:60]}...")

    print("\n" + "=" * 60)
    print(f"Host:  provider={host_config.get('provider')} | voice_id={host_config.get('voice_id')} | dialect={host_config.get('dialect')} | gender={host_config.get('gender')}")
    print(f"Guest: provider={guest_config.get('provider')} | voice_id={guest_config.get('voice_id')} | dialect={guest_config.get('dialect')} | gender={guest_config.get('gender')}")
    print(f"Speed: {speed}x")
    print("=" * 60)

    combined_audio = None
    silence = AudioSegment.silent(duration=500)
    results = []

    for i, item in enumerate(script):
        speaker = item['speaker']
        text = item['text']
        config = host_config if speaker == 'host' else guest_config
        speaker_name = "Host" if speaker == 'host' else "Guest"

        print(f"\n[{i+1}] {speaker_name}:")
        print(f"   Text: {text[:80]}...")

        result = await text_to_speech(
            text=text,
            provider=config.get('provider', 'auto'),
            language=config.get('language', 'auto'),
            dialect=config.get('dialect', 'fusha'),
            gender=config.get('gender', 'male'),
            style=config.get('style', 'professional'),
            speed=speed,
            voice_id=config.get('voice_id'),
        )

        if not result.get('success'):
            print(f"   Failed: {result.get('error')}")
            continue

        try:
            audio_bytes = requests.get(result['audio_url']).content
            audio_segment = load_audio_safely(audio_bytes)
        except Exception as e:
            print(f"   Decode failed: {e}")
            continue

        if combined_audio is None:
            combined_audio = audio_segment + silence
        else:
            combined_audio += silence + audio_segment + silence

        results.append({
            'index': i,
            'speaker': speaker,
            'duration': result.get('duration', 0),
            'voice': result.get('voice'),
        })

        print(f"   Generated ({result.get('duration', 0):.2f} sec) - Voice: {result.get('voice')}")

    if combined_audio is None:
        return {'success': False, 'error': 'No audio generated'}

    # Export the final podcast as MP3
    output_buffer = io.BytesIO()
    combined_audio.export(output_buffer, format="mp3", bitrate="128k")
    output_buffer.seek(0)

    upload_result = upload_to_cloudinary(output_buffer.getvalue(), '.mp3')

    if upload_result['success']:
        print("\n" + "=" * 60)
        print("Podcast generated successfully!")
        print(f"   Total turns: {len(results)}")
        print(f"   Total duration: {upload_result['duration']:.2f} sec")
        print(f"   URL: {upload_result['url']}")
        print("=" * 60)

        return {
            'success': True,
            'audio_url': upload_result['url'],
            'duration': upload_result['duration'],
            'sentences_count': len(results),
            'details': results,
        }
    else:
        return {'success': False, 'error': upload_result.get('error')}
