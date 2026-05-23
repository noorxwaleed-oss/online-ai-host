from fastapi import FastAPI , Query
from pydantic import BaseModel 
from fastapi.middleware.cors import CORSMiddleware
from storage_services import current_time, generate_id
from utils import detect_input_type, parse_script_for_save



class multiAgent(BaseModel):
    host_name: str
    host_gender: str
    guest_name: str
    guest_gender: str
    podcast_name: str
    language: str
    content :str
    voice_id_host: str
    voice_id_guest: str
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
                          voice_id_guest: str , host_style: str, guest_style: str , user_id: str):
    try:

 #=====================================================
      # content_analyzer agnet 
      # user_id = generate_id()

    
      

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

      from utils import tojson ,to_str_script
     
      json_script = tojson(script)
      script_str = to_str_script(json_script)
      # Script
      print(f"\n🎬 Generated Script:\n{script_str}")
  #=====================================================
    # store the script in Cloudinary and get the URL

      from storage_services import create_project, save_agent_output, save_input
      dic_script = parse_script_for_save(script_str)
      project = create_project(user_id) 
      project_id =  project["project_id"]  
      content_type = detect_input_type(content)
      if  content_type =='pdf':
          pdf_path = content
          source_url = None
      elif content_type =='url':
          pdf_path = None
          source_url =  content 
      else:
          print(" error unknown input : please enter url or pdf ")      
      save_input(user_id, project_id,content_type,pdf_path,source_url)
      savedscript = save_agent_output(user_id, project_id, "script",dic_script)
    
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
      result_audio = await generate_podcast_from_script(
          raw_text= script_str,
          host_config=host_config,
          guest_config=guest_config,
          speed=1.0,  # Normal speed
      )

      print(f"\n🎉 Final Result:")
      print(f"   Success: {result_audio.get('success')}")
      print(f"   Audio URL: {result_audio.get('audio_url')}")
      print(f"   Total duration: {result_audio.get('duration', 0):.2f} seconds")

      if result_audio.get('audio_url'):
          import requests
          from IPython.display import Audio, display
          response = requests.get(result_audio['audio_url'])
          # display(Audio(response.content))
      message = "Podcast generated successfully!" if result_audio.get('success') else "Failed to generate podcast."
      audio_output = {"message": message, "audio_url": result_audio.get('audio_url'), "duration": result_audio.get('duration', 0)}
      # return {"message": message, "audio_url": result_audio.get('audio_url'), "duration": result_audio.get('duration', 0)}


      #======================================================
      # save oudio agent
      from storage_services import save_audio_output
      save_audio_output(user_id, project_id, result_audio['audio_url']  )






      # ======================================================


      from cover_agent import CoverArtAgent


      # with open(content, "r", encoding="utf-8") as f:
      #     metadata = json.load(f)

      
      # =========================
      # GENERATE IMAGE
      # =========================

      agent = CoverArtAgent()

      image = agent.generate(
          metadata=key_points_dict,
          style="Colorful",
          aspect_ratio="2:3"
      )

      image.show()
      # ======================================================


      # save cover_art agent
      from storage_services import save_cover_output
      coverArt_output = save_cover_output(user_id , project_id , image)

      # ======================================================
      # publishing agent 
      from pub_models import EpisodeAssets, PodcastInfo, PublishingInput
      from publishing_agent import PublishingAgent
      from storage_services import get_feed_url, save_feed_url


      existing_feed = get_feed_url(user_id)

      result = PublishingAgent().publish(
          PublishingInput(
              episode=EpisodeAssets(
                  script_id = savedscript['public_id'],  # from Cell 14
                  title=title,  # from Cell 5
                  description=key_points_dict['topics'][0].get('insight', 'AI-generated podcast episode'),
                  audio_url= result_audio['audio_url'],        # from Cell 16
                  cover_image_url= coverArt_output["image_url"],  # from Cell 3
                  duration_seconds=int(result_audio.get('duration', 0)),
              ),
              podcast=PodcastInfo(
                  podcast_title="AI Host Interview",
                  podcast_description="AI-generated podcast interviews on trending topics.",
                  author=user_id,
                  language="ar",
                  category="Technology",
                  cover_image_url= coverArt_output["image_url"],
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


      from storage_services import list_user_projects
      list_user_projects(user_id)
  #======================================================
    #   # Retrieve and save metadata    
    #   from storage_services import get_project_metadata, save_metadata
    #   metadata =   get_project_metadata(user_id, project_id)
    #   saved_meatadata = save_metadata(metadata, user_id,  project_id)
    #   print(saved_meatadata)
      return audio_output
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
    





    # ========================================================



