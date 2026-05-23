import json
from backend.core.logger import logger
from backend.schemas.podcast import PodcastCreate, PodcastResponse
from backend.services.storage_service import (
    create_project, save_input, save_agent_output, 
    save_audio_output, save_cover_output, get_feed_url, save_feed_url
)
from backend.utils.helpers import (
    detect_input_type, parse_script_for_save, tojson, to_str_script
)
from backend.agents.analysis_agent import agent_analyzer
from backend.agents.text_generation import textGeneration_chat_chain
from backend.agents.audio_agent import generate_podcast_from_script
from backend.agents.cover_agent import CoverArtAgent
from backend.agents.publishing_agent import PublishingAgent
from backend.models.publishing import PublishingInput, EpisodeAssets, PodcastInfo

async def process_podcast_pipeline(data: PodcastCreate) -> PodcastResponse:
    try:
        logger.info(f"Starting podcast pipeline for user: {data.user_id}")
        
        # 1. Content Analysis
        key_points_json = agent_analyzer(data.content, data.language)
        key_points_dict = json.loads(key_points_json)
        title = key_points_dict['topics'][0]['title']
        
        # 2. Text Generation
        script_output = textGeneration_chat_chain.invoke({
            "key_points": key_points_json,
            "podcast_name": data.podcast_name,
            "host_name": data.host_name,
            "host_gender": data.host_gender,
            "guest_name": data.guest_name,
            "guest_gender": data.guest_gender,
        })
        
        json_script = tojson(script_output)
        script_str = to_str_script(json_script)
        
        # 3. Storage & Setup
        project = create_project(data.user_id)
        project_id = project["project_id"]
        content_type = detect_input_type(data.content)
        
        pdf_path = data.content if content_type == 'pdf' else None
        source_url = data.content if content_type == 'url' else None
        
        save_input(data.user_id, project_id, content_type, pdf_path, source_url)
        dic_script = parse_script_for_save(script_str)
        saved_script = save_agent_output(data.user_id, project_id, "script", dic_script)
        
        # 4. Audio Generation
        provider = 'elevenlabs' if data.language.lower() == 'english' else 'munsit'
        lang = 'en' if data.language.lower() == 'english' else 'ar'
        
        host_config = {
            'provider': provider, 'language': lang, 'gender': data.host_gender,
            'style': data.host_style, 'voice_id': data.voice_id_host
        }
        guest_config = {
            'provider': provider, 'language': lang, 'gender': data.guest_gender,
            'style': data.guest_style, 'voice_id': data.voice_id_guest
        }
        
        result_audio = await generate_podcast_from_script(
            raw_text=script_str,
            host_config=host_config,
            guest_config=guest_config,
            speed=1.0
        )
        
        if not result_audio.get('success'):
            raise Exception("Audio generation failed")
            
        save_audio_output(data.user_id, project_id, result_audio['audio_url'])
        
        # 5. Cover Art
        cover_agent = CoverArtAgent()
        image = cover_agent.generate(metadata=key_points_dict, style="Colorful", aspect_ratio="2:3")
        cover_output = save_cover_output(data.user_id, project_id, image)
        
        # 6. Publishing
        existing_feed = get_feed_url(data.user_id)
        pub_result = PublishingAgent().publish(
            PublishingInput(
                episode=EpisodeAssets(
                    script_id=saved_script['public_id'],
                    title=title,
                    description=key_points_dict['topics'][0].get('insight', 'AI-generated podcast episode'),
                    audio_url=result_audio['audio_url'],
                    cover_image_url=cover_output["image_url"],
                    duration_seconds=int(result_audio.get('duration', 0)),
                ),
                podcast=PodcastInfo(
                    podcast_title="AI Host Interview",
                    podcast_description="AI-generated podcast interviews on trending topics.",
                    author=data.user_id,
                    language="ar",
                    category="Technology",
                    cover_image_url=cover_output["image_url"],
                ),
                existing_feed_url=existing_feed,
            ),
            user_id=data.user_id,
        )
        
        if pub_result.success:
            save_feed_url(data.user_id, pub_result.feed_url)
            
        return PodcastResponse(
            message="Podcast generated successfully!",
            audio_url=result_audio.get('audio_url'),
            duration=result_audio.get('duration', 0)
        )
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        return PodcastResponse(message="Failed to generate podcast.", error=str(e))
