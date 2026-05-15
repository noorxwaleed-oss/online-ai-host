import io
import requests
import re
from pydub import AudioSegment
from typing import Dict, Any
from audio import text_to_speech

from utils import upload_to_cloudinary
def parse_script(raw_text: str) -> list:
    """
    تحليل النص التلقائي إلى جولات Host و Guest

    يدعم صيغ:
    - Host: النص...
    - Guest: النص...
    - أو host: ... (غير حساس لحالة الأحرف)
    """
    lines = raw_text.strip().split('\n')
    script = []
    current_speaker = None
    current_text = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # search (Host: أو Guest:)
        host_match = re.match(r'^(?:Host|HOST|host)\s*:\s*(.*)$', line)
        guest_match = re.match(r'^(?:Guest|GUEST|guest)\s*:\s*(.*)$', line)

        if host_match:
            # save current text
            if current_speaker and current_text:
                script.append({
                    'speaker': current_speaker,
                    'text': current_text.strip()
                })
            current_speaker = 'host'
            current_text = host_match.group(1)

        elif guest_match:
            if current_speaker and current_text:
                script.append({
                    'speaker': current_speaker,
                    'text': current_text.strip()
                })
            current_speaker = 'guest'
            current_text = guest_match.group(1)

        else:

            if current_speaker:
                current_text += " " + line


    if current_speaker and current_text:
        script.append({
            'speaker': current_speaker,
            'text': current_text.strip()
        })

    return script


async def generate_podcast_from_script(
    raw_text: str,
    host_config: Dict[str, Any],
    guest_config: Dict[str, Any],
    speed: float = 1.0
) -> Dict[str, Any]:
    """
    توليد بودكاست كامل من نص خام (مع Host: و Guest:)

    host_config = {
        'provider': 'munsit', 'language': 'ar', 'dialect': 'saudi',
        'gender': 'male', 'style': 'professional'
    }

    guest_config = {
        'provider': 'munsit', 'language': 'ar', 'dialect': 'kuwaiti',
        'gender': 'male', 'style': 'energetic'
    }
    """

    # Text analysis into rounds
    script = parse_script(raw_text)

    if not script:
        return {'success': False, 'error': 'No valid script found. Make sure to use "Host:" and "Guest:" labels.'}

    print("="*60)
    print("🎙️ Parsing Script")
    print(f"   Total sentences detected: {len(script)}")
    print("="*60)

    for i, item in enumerate(script):
        print(f"   [{i+1}] {item['speaker'].upper()}: {item['text'][:60]}...")

    print("\n" + "="*60)
    print(f"🎙️ Host Config: {host_config.get('dialect')} | {host_config.get('gender')} | {host_config.get('style')}")
    print(f"👤 Guest Config: {guest_config.get('dialect')} | {guest_config.get('gender')} | {guest_config.get('style')}")
    print(f"⚡ Speed: {speed}x")
    print("="*60)

    combined_audio = None
    silence = AudioSegment.silent(duration=500)  # صمت نصف ثانية بين الجمل
    results = []
    total_duration = 0

    for i, item in enumerate(script):
        speaker = item['speaker']
        text = item['text']

        # Selecting settings according to the speaker
        if speaker == 'host':
            config = host_config
            speaker_name = "Host"
        else:
            config = guest_config
            speaker_name = "Guest"

        print(f"\n📢 [{i+1}] {speaker_name}:")
        print(f"   Text: {text[:80]}...")

        # Generate speech
        result = await text_to_speech(
            text=text,
            provider=config.get('provider', 'auto'),
            language=config.get('language', 'auto'),
            dialect=config.get('dialect', 'fusha'),
            gender=config.get('gender', 'male'),
            style=config.get('style', 'professional'),
            speed=speed
        )

        if not result.get('success'):
            print(f"   ❌ Failed: {result.get('error')}")
            continue

        # Download audio
        audio_bytes = requests.get(result['audio_url']).content
        audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))

        # Added to the final file
        if combined_audio is None:
            combined_audio = audio_segment + silence
        else:
            combined_audio += silence + audio_segment + silence

        total_duration += result.get('duration', 0)
        results.append({
            'index': i,
            'speaker': speaker,
            'duration': result.get('duration', 0),
            'voice': result.get('voice')
        })

        print(f"   ✅ Generated ({result.get('duration', 0):.2f} sec) - Voice: {result.get('voice')}")

    if combined_audio is None:
        return {'success': False, 'error': 'No audio generated'}

    # Upload the final file
    output_buffer = io.BytesIO()
    combined_audio.export(output_buffer, format="mp3")
    output_buffer.seek(0)

    upload_result = upload_to_cloudinary(output_buffer.getvalue(), '.mp3')

    if upload_result['success']:
        print("\n" + "="*60)
        print("✅ Podcast generated successfully!")
        print(f"   Total sentences: {len(results)}")
        print(f"   Total duration: {upload_result['duration']:.2f} sec")
        print(f"   URL: {upload_result['url']}")
        print("="*60)

        return {
            'success': True,
            'audio_url': upload_result['url'],
            'duration': upload_result['duration'],
            'sentences_count': len(results),
            'details': results
        }
    else:
        return {'success': False, 'error': upload_result.get('error')}

print("✅ generate_podcast_from_script function ready!")