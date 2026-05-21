from fastapi import FastAPI , Query
from pydantic import BaseModel 
from fastapi.middleware.cors import CORSMiddleware



class multiAgent(BaseModel):
    host_name: str
    host_gender: str
    guest_name: str
    guest_gender: str
    podcast_name: str
    tone: str
    speech_speed: int
    video_duration: int
    language: str
    content :str
    voice_id: str
    host_style: str
    guest_style: str
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def get_podcast_details(host_name: str, host_gender: str, guest_name: str, guest_gender: str, 
                        podcast_name: str, tone: str, speech_speed: int, video_duration: int,
                          language: str, content: str , voice_id_host: str, voice_id_guest: str , host_style: str, guest_style: str):
    from content_analyzer import agent_analyzer
    from audio import generate_podcast_from_script
    import json
    from chat import textGeneration_chat_chain 
    content  = agent_analyzer (content ,language)
    content_dict = json.loads(content)
    script = textGeneration_chat_chain.invoke({
        "key_points": content,
        "tone": tone,
        "speech_speed":speech_speed ,
        "video_duration": video_duration,
        "podcast_name": podcast_name,
        "host_name": host_name,
        "host_gender": host_gender,
        "guest_name": guest_name,
        "guest_gender": guest_gender,
    })
    from utils import tojson 
    from utils import to_str_script 
    script = tojson(script)
    script_str = to_str_script(script)
    print(type(script_str))
    print(script_str)
    # Script
    


    raw_script = script_str
    provider = 'elevenlabs' if language.lower() == 'english' else 'munsit'
    lang = 'en' if language.lower() == 'english' else 'ar'
    print(f"<<<<<<<<<<<<<<<<<<<Selected TTS Provider: {provider}"f"Language: {lang}>>>>>>>>>>>>>>>>>>>")
    # Host = Saudi Najdi male voice (Munsit)
    host_config = {
        'provider': provider,
        'language': lang,
        'gender':  host_gender,
        'style': host_style,
        'voice_id': voice_id_host
    }

    # Guest = Egyptian male voice (Munsit) — different voice
    # {"id": "ar-najdi-female-1", "name": "Maha", "gender": "female", "dialect": "saudi", "style": "calm"}
    guest_config = {
        'provider': provider,
        'language': lang,
        'gender': guest_gender,
        'style': guest_style,
        'voice_id': voice_id_guest
    }

    # Generate podcast
    result = await generate_podcast_from_script(
        raw_text=raw_script,
        host_config=host_config,
        guest_config=guest_config,
        speed=speech_speed
    )

    print(f"\n🎉 Final Result:")
    print(f"   Success: {result.get('success')}")
    print(f"   Audio URL: {result.get('audio_url')}")
    print(f"   Total duration: {result.get('duration', 0):.2f} seconds")

    if result.get('audio_url'):
        import requests
        from IPython.display import Audio, display
        response = requests.get(result['audio_url'])
        # display(Audio(response.content))
    message = "Podcast generated successfully!" if result.get('success') else "Failed to generate podcast."
    # {"message": message, "audio_url": result.get('audio_url'), "duration": result.get('duration', 0)}
    return {"message": message, "audio_url": result.get('audio_url'), "duration": result.get('duration', 0)}



