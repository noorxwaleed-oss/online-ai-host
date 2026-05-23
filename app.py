from fastapi import FastAPI , Query
from pydantic import BaseModel 
from fastapi.middleware.cors import CORSMiddleware



class multiAgent(BaseModel):
    host_name: str
    host_gender: str
    guest_name: str
    guest_gender: str
    podcast_name: str
    language: str
    content :str
    voice_id: str
    host_style: str
    guest_style: str
    user_id: str
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def get_podcast_details(host_name: str, host_gender: str, guest_name: str, guest_gender: str, 
                        podcast_name: str, language: str, content: str , voice_id_host: str,
                          voice_id_guest: str , host_style: str, guest_style: str, user_id: str):
    try:
 #=====================================================
      # content_analyzer agnet 
      from content_analyzer import agent_analyzer
      from audio import generate_podcast_from_script
      import json
      from chat import textGeneration_chat_chain 
      key_points = agent_analyzer (content ,language)
      key_points_dict = json.loads(key_points)
      title = key_points_dict['topics'][0]['title']
  #=====================================================
      # text generation agent
      script = textGeneration_chat_chain.invoke({
          "key_points": key_points,
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
      # Script
      print(f"\n🎬 Generated Script:\n{script_str}")
  #=====================================================
      # store the script in Cloudinary 
      from storage_service import create_project, save_input, save_script
      
      project_ID = create_project(user_id)
      save_input(user_id, project_ID, "pdf_path", pdf_path = content)
      saved_script = save_script(script_json=script_str, user_id=user_id, project_id=project_ID)
      print(f"\n💾 Script saved to Cloudinary: {saved_script['url']}")
  #=====================================================
      #  audio generation agent
      provider = 'elevenlabs' if language.lower() == 'english' else 'munsit'
      lang = 'en' if language.lower() == 'english' else 'ar'
      
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
          raw_text= script_str,
          host_config=host_config,
          guest_config=guest_config,
          speed=1.0,  # Normal speed
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
      audio_output = {"message": message, "audio_url": result.get('audio_url'), "duration": result.get('duration', 0)}
      # return {"message": message, "audio_url": result.get('audio_url'), "duration": result.get('duration', 0)}


      #======================================================
      # publishing agent 
      from pub_models import EpisodeAssets, PodcastInfo, PublishingInput
      from publishing_agent import PublishingAgent
      from storage_service import get_feed_url, save_feed_url


      existing_feed = get_feed_url(user_id)

      result = PublishingAgent().publish(
          PublishingInput(
              episode=EpisodeAssets(
                  script_id =saved_script['public_id'],  # from Cell 14
                  title=title,  # from Cell 5
                  description=key_points_dict['topics'][0].get('insight', 'AI-generated podcast episode'),
                  audio_url=result['audio_url'],        # from Cell 16
                  cover_image_url="https://res.cloudinary.com/duxc6oeju/image/upload/v1779454098/IMG-20260522-WA0015_dwdfqn.jpg",  # from Cell 3
                  duration_seconds=int(result.get('duration', 0)),
              ),
              podcast=PodcastInfo(
                  podcast_title="AI Host Interview",
                  podcast_description="AI-generated podcast interviews on trending topics.",
                  author=user_id,
                  language="ar",
                  category="Technology",
                  cover_image_url="https://res.cloudinary.com/duxc6oeju/image/upload/v1779454098/IMG-20260522-WA0015_dwdfqn.jpg",
              ),
              existing_feed_url= existing_feed,
          ),
          user_id=user_id,
      )

      if result.success:
          save_feed_url(user_id, result.feed_url)
          print(f"Published! Feed URL: {result.feed_url}")
          print(f"Episodes in feed: {result.episode_count}")
      else:
          print(f"Publishing failed: {result.error_message}")


      from storage_service import list_user_projects
      list_user_projects(user_id)
  #======================================================
      # Retrieve and save metadata    
      from storage_service import get_project_metadata, save_metadata
      metadata =   get_project_metadata(user_id, project_ID)
      saved_meatadata = save_metadata(metadata, user_id, project_ID)
      print(saved_meatadata)
      return audio_output
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}


