import os
import tempfile
import io
import httpx
import requests
from typing import Dict, Any
from gtts import gTTS
from pydub import AudioSegment
from backend.config.settings import settings
from backend.agents.prompts import ENGLISH_VOICES, STYLES, MODEL_ID
from backend.utils.helpers import parse_script_turns
from backend.cloudinary.config import cloudinary_config
import cloudinary.uploader
import uuid

# Key rotation logic
ELEVENLABS_CURRENT_INDEX = 0
def get_elevenlabs_key():
    keys = settings.ELEVENLABS_KEYS
    if not keys: return None
    global ELEVENLABS_CURRENT_INDEX
    return keys[ELEVENLABS_CURRENT_INDEX]

def rotate_elevenlabs_key():
    global ELEVENLABS_CURRENT_INDEX
    keys = settings.ELEVENLABS_KEYS
    if not keys: return None
    ELEVENLABS_CURRENT_INDEX = (ELEVENLABS_CURRENT_INDEX + 1) % len(keys)
    return get_elevenlabs_key()

MUNSIT_CURRENT_INDEX = 0
def get_munsit_key():
    keys = settings.MUNSIT_KEYS
    if not keys: return None
    global MUNSIT_CURRENT_INDEX
    return keys[MUNSIT_CURRENT_INDEX]

def rotate_munsit_key():
    global MUNSIT_CURRENT_INDEX
    keys = settings.MUNSIT_KEYS
    if not keys: return None
    MUNSIT_CURRENT_INDEX = (MUNSIT_CURRENT_INDEX + 1) % len(keys)
    return get_munsit_key()

def _detect_audio_ext(audio_bytes: bytes) -> str:
    if len(audio_bytes) < 12: return '.mp3'
    if audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE': return '.wav'
    if audio_bytes[:3] == b'ID3': return '.mp3'
    if audio_bytes[0] == 0xFF and (audio_bytes[1] & 0xE0) == 0xE0: return '.mp3'
    if audio_bytes[:4] == b'OggS': return '.ogg'
    if audio_bytes[:4] == b'fLaC': return '.flac'
    if audio_bytes[4:8] == b'ftyp': return '.m4a'
    return '.mp3'

def upload_to_cloudinary_util(audio_bytes: bytes, file_ext: str = None) -> Dict[str, Any]:
    detected_ext = _detect_audio_ext(audio_bytes)
    if file_ext is None: file_ext = detected_ext
    filename = f"temp_audio_{uuid.uuid4()}{file_ext}"
    with open(filename, 'wb') as f:
        f.write(audio_bytes)
    try:
        upload_result = cloudinary.uploader.upload(filename, folder="podcast_audio", resource_type="auto")
        return {'success': True, 'url': upload_result.get('secure_url'), 'duration': upload_result.get('duration', 0), 'format': file_ext.lstrip('.')}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        if os.path.exists(filename): os.remove(filename)

def load_audio_safely(audio_bytes: bytes):
    ext = _detect_audio_ext(audio_bytes).lstrip('.')
    fmt_map = {'mp3': 'mp3', 'wav': 'wav', 'ogg': 'ogg', 'flac': 'flac', 'm4a': 'mp4'}
    fmt = fmt_map.get(ext, 'mp3')
    return AudioSegment.from_file(io.BytesIO(audio_bytes), format=fmt)

async def text_to_speech(text: str, provider: str = "auto", language: str = "auto", dialect: str = "fusha", gender: str = "male", style: str = "professional", speed: float = 1.0, voice_id: str = None) -> Dict[str, Any]:
    if not text or not text.strip(): return {'success': False, 'error': 'Text cannot be empty'}
    if language == "auto":
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        final_language = 'ar' if arabic_chars > len(text) * 0.3 else 'en'
    else: final_language = language

    final_provider = provider
    if final_provider == "auto":
        if final_language == 'ar': final_provider = 'munsit' if settings.MUNSIT_KEYS else 'gtts'
        else: final_provider = 'elevenlabs' if settings.ELEVENLABS_KEYS else 'gtts'

    if final_provider == 'gtts':
        lang_code = 'ar' if final_language == 'ar' else 'en'
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp: tmp_path = tmp.name
        tts = gTTS(text=text, lang=lang_code, slow=(speed < 0.8))
        tts.save(tmp_path)
        with open(tmp_path, 'rb') as f: audio_bytes = f.read()
        os.unlink(tmp_path)
        upload_result = upload_to_cloudinary_util(audio_bytes, '.mp3')
        if upload_result['success']:
            return {'success': True, 'audio_url': upload_result['url'], 'duration': upload_result['duration'], 'provider': 'gtts', 'voice': 'gTTS', 'language': final_language}
        return {'success': False, 'error': upload_result.get('error')}

    elif final_provider == 'munsit':
        voice_id_to_use = voice_id or ('ar-najdi-male-2' if gender == 'male' else 'ar-najdi-female-1')
        for attempt in range(len(settings.MUNSIT_KEYS)):
            api_key = get_munsit_key()
            if not api_key: break
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post("https://api.munsit.com/api/v1/text-to-speech/faseeh-v1-preview", headers={"x-api-key": api_key, "Content-Type": "application/json"}, json={"text": text, "voice_id": voice_id_to_use, "speed": speed})
                    if response.status_code == 200:
                        audio_bytes = response.content
                        upload_result = upload_to_cloudinary_util(audio_bytes, '.mp3')
                        if upload_result['success']:
                            return {'success': True, 'audio_url': upload_result['url'], 'duration': upload_result['duration'], 'provider': 'munsit', 'voice': voice_id_to_use, 'language': final_language}
                    rotate_munsit_key()
            except: rotate_munsit_key()
        return await text_to_speech(text, provider='gtts', language=final_language)

    elif final_provider == 'elevenlabs':
        from elevenlabs.client import ElevenLabs
        selected_voice = next((v for v in ENGLISH_VOICES.values() if v['gender'] == gender and v['style'] == style), next((v for v in ENGLISH_VOICES.values() if v['gender'] == gender), ENGLISH_VOICES['adam']))
        style_settings = STYLES.get(style, STYLES["professional"])
        for attempt in range(len(settings.ELEVENLABS_KEYS)):
            api_key = get_elevenlabs_key()
            if not api_key: break
            try:
                client = ElevenLabs(api_key=api_key)
                audio_generator = client.text_to_speech.convert(text=text, voice_id=selected_voice['id'], model_id=MODEL_ID, output_format="mp3_44100_128", voice_settings={"stability": style_settings["stability"], "similarity_boost": style_settings["similarity_boost"]})
                audio_bytes = b"".join(chunk for chunk in audio_generator)
                upload_result = upload_to_cloudinary_util(audio_bytes, '.mp3')
                if upload_result['success']:
                    return {'success': True, 'audio_url': upload_result['url'], 'duration': upload_result['duration'], 'provider': 'elevenlabs', 'voice': selected_voice['name'], 'language': final_language}
                rotate_elevenlabs_key()
            except: rotate_elevenlabs_key()
        return await text_to_speech(text, provider='gtts', language=final_language)
    return {'success': False, 'error': f'Unknown provider: {final_provider}'}

async def generate_podcast_from_script(raw_text: str, host_config: Dict[str, Any], guest_config: Dict[str, Any], speed: float = 1.0) -> Dict[str, Any]:
    script = parse_script_turns(raw_text)
    if not script: return {'success': False, 'error': 'No valid script found.'}
    combined_audio = None
    silence = AudioSegment.silent(duration=500)
    results = []
    for i, item in enumerate(script):
        speaker = item['speaker']
        text = item['text']
        config = host_config if speaker == 'host' else guest_config
        result = await text_to_speech(text=text, provider=config.get('provider', 'auto'), language=config.get('language', 'auto'), dialect=config.get('dialect', 'fusha'), gender=config.get('gender', 'male'), style=config.get('style', 'professional'), speed=speed, voice_id=config.get('voice_id'))
        if not result.get('success'): continue
        try:
            audio_bytes = requests.get(result['audio_url']).content
            audio_segment = load_audio_safely(audio_bytes)
        except: continue
        if combined_audio is None: combined_audio = audio_segment + silence
        else: combined_audio += silence + audio_segment + silence
        results.append({'index': i, 'speaker': speaker, 'duration': result.get('duration', 0), 'voice': result.get('voice')})
    if combined_audio is None: return {'success': False, 'error': 'No audio generated'}
    output_buffer = io.BytesIO()
    combined_audio.export(output_buffer, format="mp3", bitrate="128k")
    upload_result = upload_to_cloudinary_util(output_buffer.getvalue(), '.mp3')
    if upload_result['success']:
        return {'success': True, 'audio_url': upload_result['url'], 'duration': upload_result['duration'], 'sentences_count': len(results), 'details': results}
    return {'success': False, 'error': upload_result.get('error')}
