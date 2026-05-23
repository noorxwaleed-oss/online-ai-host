import sys
import cloud_config  # initializes Cloudinary
from storage_service import (
    create_project,
    save_input,
    save_script,
    save_metadata,
    save_feed_url,
    get_feed_url,
)

# Agent imports — adjust paths based on your folder structure
sys.path.insert(0, "agents/content_analyzer")
sys.path.insert(0, "agents/text_generation")
sys.path.insert(0, "agents/audio")
sys.path.insert(0, "agents/publishing")


def run_pipeline(user_id: str):
    project = create_project(user_id)
    project_id = project["project_id"]

    print(f"Project created: {project_id}")

    # Upload source input
    input_data = save_input(
        user_id=user_id,
        project_id=project_id,
        input_type="pdf",
        pdf_path="sample.pdf",
    )
    print(f"Input saved: {input_data.get('pdf_url')}")

    # 1. Content Analysis Agent
    # from chat import content_analysis_chain
    # analysis = content_analysis_chain.invoke({"pdf_url": input_data["pdf_url"]})
    analysis = {"title": "Demo Episode", "summary": "Demo summary", "key_points": []}  # placeholder
    print("Content analysis done")

    # 2. Text Generation Agent
    # from chat import textGeneration_chat_chain
    # script = textGeneration_chat_chain.invoke({
    #     "key_points": analysis["key_points"],
    #     "tone": "casual",
    #     "speech_speed": 1,
    #     "video_duration": 900,
    # })
    script = {"turns": []}  # placeholder
    print("Script generated")

    # 3. Save script to Cloudinary
    script_result = save_script(script, user_id, project_id)
    print(f"Script saved: {script_result['url']}")

    # 4. Audio Production Agent
    # from audio_agent import text_to_speech
    # audio = await text_to_speech(text=script_text, provider="auto", language="auto")
    audio = {"audio_url": "https://example.com/audio.mp3", "duration": 900}  # placeholder
    print("Audio produced")

    # 5. Publishing Agent — generate/update RSS feed
    from publishing_agent import PublishingAgent
    from pub_models import PublishingInput, EpisodeAssets, PodcastInfo

    previous_feed_url = get_feed_url(user_id)

    pub_result = PublishingAgent().publish(
        PublishingInput(
            episode=EpisodeAssets(
                script_id=script_result["public_id"],
                title=analysis["title"],
                description=analysis["summary"],
                audio_url=audio["audio_url"],
                cover_image_url="https://example.com/cover.jpg",  # from cover agent
                duration_seconds=audio.get("duration"),
            ),
            podcast=PodcastInfo(
                podcast_title="AI Host Interview",
                podcast_description="AI-generated podcast interviews on trending topics.",
                author=user_id,
                language="ar",
                category="Technology",
                cover_image_url="https://example.com/podcast_cover.jpg",
            ),
            existing_feed_url=previous_feed_url,
        ),
        user_id=user_id,
    )

    if pub_result.success:
        save_feed_url(user_id, pub_result.feed_url)
        print(f"Published! Feed URL: {pub_result.feed_url}")
        print(f"Episodes in feed: {pub_result.episode_count}")
    else:
        print(f"Publishing failed: {pub_result.error_message}")

    # 6. Save metadata
    metadata = {
        "user_id": user_id,
        "project_id": project_id,
        "analysis": analysis,
        "script": script_result,
        "audio": audio,
        "publishing": pub_result.model_dump() if pub_result.success else {"error": pub_result.error_message},
    }

    final_url = save_metadata(metadata, user_id, project_id)
    print(f"DONE: {final_url}")


if __name__ == "__main__":
    run_pipeline("demo_user")
