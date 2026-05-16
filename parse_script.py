# import io
# import requests
# import re
# from audio import _detect_audio_ext, text_to_speech
# from pydub import AudioSegment
# from typing import Dict, Any


# from utils import upload_to_cloudinary
# def parse_script(raw_text: str) -> list:
#     """Parse raw text into Host/Guest turns."""
#     lines = raw_text.strip().split('\n')
#     script = []
#     current_speaker = None
#     current_text = ""

#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue

#         host_match = re.match(r'^(?:Host|HOST|host)\s*:\s*(.*)$', line)
#         guest_match = re.match(r'^(?:Guest|GUEST|guest)\s*:\s*(.*)$', line)

#         if host_match:
#             if current_speaker and current_text:
#                 script.append({'speaker': current_speaker, 'text': current_text.strip()})
#             current_speaker = 'host'
#             current_text = host_match.group(1)
#         elif guest_match:
#             if current_speaker and current_text:
#                 script.append({'speaker': current_speaker, 'text': current_text.strip()})
#             current_speaker = 'guest'
#             current_text = guest_match.group(1)
#         else:
#             if current_speaker:
#                 current_text += " " + line

#     if current_speaker and current_text:
#         script.append({'speaker': current_speaker, 'text': current_text.strip()})

#     return script


# def _load_audio_safely(audio_bytes: bytes) -> AudioSegment:
#     """Load an AudioSegment by detecting the actual format from bytes."""
#     ext = _detect_audio_ext(audio_bytes).lstrip('.')
#     fmt_map = {'mp3': 'mp3', 'wav': 'wav', 'ogg': 'ogg', 'flac': 'flac', 'm4a': 'mp4'}
#     fmt = fmt_map.get(ext, 'mp3')
#     return AudioSegment.from_file(io.BytesIO(audio_bytes), format=fmt)


# async def generate_podcast_from_script(
#     raw_text: str,
#     host_config: Dict[str, Any],
#     guest_config: Dict[str, Any],
#     speed: float = 1.0
# ) -> Dict[str, Any]:
#     """Generate a full podcast from a raw Host:/Guest: script."""

#     script = parse_script(raw_text)

#     if not script:
#         return {'success': False, 'error': 'No valid script found. Use "Host:" and "Guest:" labels.'}

#     print("="*60)
#     print("🎙️ Parsing Script")
#     print(f"   Total turns detected: {len(script)}")
#     print("="*60)

#     for i, item in enumerate(script):
#         print(f"   [{i+1}] {item['speaker'].upper()}: {item['text'][:60]}...")

#     print("\n" + "="*60)
#     print(f"🎙️ Host:  provider={host_config.get('provider')} | voice_id={host_config.get('voice_id')} | dialect={host_config.get('dialect')} | gender={host_config.get('gender')}")
#     print(f"👤 Guest: provider={guest_config.get('provider')} | voice_id={guest_config.get('voice_id')} | dialect={guest_config.get('dialect')} | gender={guest_config.get('gender')}")
#     print(f"⚡ Speed: {speed}x")
#     print("="*60)

#     combined_audio = None
#     silence = AudioSegment.silent(duration=500)
#     results = []

#     for i, item in enumerate(script):
#         speaker = item['speaker']
#         text = item['text']

#         if speaker == 'host':
#             config = host_config
#             speaker_name = "Host"
#         else:
#             config = guest_config
#             speaker_name = "Guest"

#         print(f"\n📢 [{i+1}] {speaker_name}:")
#         print(f"   Text: {text[:80]}...")

#         result = await text_to_speech(
#             text=text,
#             provider=config.get('provider', 'auto'),
#             language=config.get('language', 'auto'),
#             dialect=config.get('dialect', 'fusha'),
#             gender=config.get('gender', 'male'),
#             style=config.get('style', 'professional'),
#             speed=speed,
#             voice_id=config.get('voice_id')
#         )

#         if not result.get('success'):
#             print(f"   ❌ Failed: {result.get('error')}")
#             continue

#         try:
#             audio_bytes = requests.get(result['audio_url']).content
#             audio_segment = _load_audio_safely(audio_bytes)
#         except Exception as e:
#             print(f"   ❌ Decode failed: {e}")
#             continue

#         if combined_audio is None:
#             combined_audio = audio_segment + silence
#         else:
#             combined_audio += silence + audio_segment + silence

#         results.append({
#             'index': i,
#             'speaker': speaker,
#             'duration': result.get('duration', 0),
#             'voice': result.get('voice')
#         })

#         print(f"   ✅ Generated ({result.get('duration', 0):.2f} sec) - Voice: {result.get('voice')}")

#     if combined_audio is None:
#         return {'success': False, 'error': 'No audio generated'}

#     # Export the final podcast as MP3
#     output_buffer = io.BytesIO()
#     combined_audio.export(output_buffer, format="mp3", bitrate="128k")
#     output_buffer.seek(0)

#     upload_result = upload_to_cloudinary(output_buffer.getvalue(), '.mp3')

#     if upload_result['success']:
#         print("\n" + "="*60)
#         print("✅ Podcast generated successfully!")
#         print(f"   Total turns: {len(results)}")
#         print(f"   Total duration: {upload_result['duration']:.2f} sec")
#         print(f"   URL: {upload_result['url']}")
#         print("="*60)

#         return {
#             'success': True,
#             'audio_url': upload_result['url'],
#             'duration': upload_result['duration'],
#             'sentences_count': len(results),
#             'details': results
#         }
#     else:
#         return {'success': False, 'error': upload_result.get('error')}

# print("✅ generate_podcast_from_script function ready!")
