
import json
def tojson (text):
    
  data = json.loads(text.content)
  
  return data

def to_str_script(script):
  # print(json.dumps(script, indent=4, ensure_ascii=False))
  # print(script["total_pages"])
  script_str = ''
  # print(script["title"])
  # print(script["podcast_name"])
  # print(script["estimated_total_words"])
  # print(script["content"])
  script_str = script["content"]
  # for page in script["content"]:
  #     # print(f"Page {page['page_number']}:")
  #     # print(page["content"])
  #     script_str += f"{page['content']}\n\n"
  #     # print("\n---\n")


  return script_str


  """Utility helpers for the Audio Production Agent."""

import os
import uuid
from typing import Dict, Any

import cloudinary
import cloudinary.uploader

# from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET


# # Configure Cloudinary
# cloudinary.config(
#     cloud_name=CLOUDINARY_CLOUD_NAME,
#     api_key=CLOUDINARY_API_KEY,
#     api_secret=CLOUDINARY_API_SECRET,
# )


"""Utility helpers for the Audio Production Agent."""

import io

import re
import uuid
from typing import Dict, Any

from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET


# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)


def _detect_audio_ext(audio_bytes: bytes) -> str:
    """Detect audio container from the first few bytes."""
    if len(audio_bytes) < 12:
        return '.mp3'
    # WAV: 'RIFF....WAVE'
    if audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE':
        return '.wav'
    # MP3: ID3 tag or MPEG frame sync
    if audio_bytes[:3] == b'ID3':
        return '.mp3'
    if audio_bytes[0] == 0xFF and (audio_bytes[1] & 0xE0) == 0xE0:
        return '.mp3'
    # OGG
    if audio_bytes[:4] == b'OggS':
        return '.ogg'
    # FLAC
    if audio_bytes[:4] == b'fLaC':
        return '.flac'
    # M4A / MP4
    if audio_bytes[4:8] == b'ftyp':
        return '.m4a'
    # Default
    return '.mp3'


def upload_to_cloudinary(audio_bytes: bytes, file_ext: str = None) -> Dict[str, Any]:
    """Upload audio bytes to Cloudinary with auto format detection."""
    detected_ext = _detect_audio_ext(audio_bytes)
    if file_ext is None:
        file_ext = detected_ext
    elif file_ext != detected_ext:
        print(f"   Caller asked for {file_ext} but bytes look like {detected_ext}. Using {detected_ext}.")
        file_ext = detected_ext

    filename = f"temp_audio_{uuid.uuid4()}{file_ext}"

    with open(filename, 'wb') as f:
        f.write(audio_bytes)

    try:
        upload_result = cloudinary.uploader.upload(
            filename,
            folder="podcast_audio",
            resource_type="auto",
        )
        return {
            'success': True,
            'url': upload_result.get('secure_url'),
            'duration': upload_result.get('duration', 0),
            'format': file_ext.lstrip('.'),
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        if os.path.exists(filename):
            os.remove(filename)


def load_audio_safely(audio_bytes: bytes):
    """Load an AudioSegment by detecting the actual format from bytes."""
    from pydub import AudioSegment
    ext = _detect_audio_ext(audio_bytes).lstrip('.')
    fmt_map = {'mp3': 'mp3', 'wav': 'wav', 'ogg': 'ogg', 'flac': 'flac', 'm4a': 'mp4'}
    fmt = fmt_map.get(ext, 'mp3')
    return AudioSegment.from_file(io.BytesIO(audio_bytes), format=fmt)


def parse_script(raw_text: str) -> list:
    """Parse raw text into Host/Guest turns."""
    lines = raw_text.strip().split('\n')
    script = []
    current_speaker = None
    current_text = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        host_match = re.match(r'^(?:Host|HOST|host)\s*:\s*(.*)$', line)
        guest_match = re.match(r'^(?:Guest|GUEST|guest)\s*:\s*(.*)$', line)

        if host_match:
            if current_speaker and current_text:
                script.append({'speaker': current_speaker, 'text': current_text.strip()})
            current_speaker = 'host'
            current_text = host_match.group(1)
        elif guest_match:
            if current_speaker and current_text:
                script.append({'speaker': current_speaker, 'text': current_text.strip()})
            current_speaker = 'guest'
            current_text = guest_match.group(1)
        else:
            if current_speaker:
                current_text += " " + line

    if current_speaker and current_text:
        script.append({'speaker': current_speaker, 'text': current_text.strip()})

    return script






import bs4
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader

def load_data(source):
    if source.startswith("http"):
        loader = WebBaseLoader(
            web_path=(source,),
            bs_kwargs=dict(parse_only=bs4.SoupStrainer(name=("article", "h1", "h2", "h3", "p")))
        )
    else:
        loader = PyPDFLoader(source)
    return loader.load()
