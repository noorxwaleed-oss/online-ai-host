"""
Quick-start example for the Publishing Agent v3.0 (RSS-based).

Demonstrates:
1. Creating a new RSS feed with the first episode
2. Adding a second episode to the existing feed
3. Showing the generated XML

Usage:
    python quickstart.py
"""

from pub_models import PublishingInput, EpisodeAssets, PodcastInfo
from rss_builder import create_new_feed, add_episode_to_existing_feed, count_episodes


def main():
    # Podcast metadata (set once)
    podcast = PodcastInfo(
        podcast_title="AI Host Interview",
        podcast_description=(
            "AI-generated podcast interviews on trending topics. "
            "Powered by the Online AI Host pipeline."
        ),
        author="Online AI Host Team",
        language="ar",
        category="Technology",
        cover_image_url="https://res.cloudinary.com/duxc6oeju/covers/podcast_cover.jpg",
    )

    # Episode 1
    ep1 = EpisodeAssets(
        script_id="scr_demo_001",
        title="The Rise of Foldable Phones in 2026",
        description=(
            "Samsung's Galaxy Z Fold 7 is here. We dig into the redesigned "
            "hinge, the 23% YoY market growth, and whether the price is justified."
        ),
        audio_url="https://res.cloudinary.com/duxc6oeju/podcast_audio/ep1.mp3",
        cover_image_url="https://res.cloudinary.com/duxc6oeju/covers/ep1.jpg",
        duration_seconds=1245,
        tags=["tech", "smartphones", "samsung"],
    )

    # Step 1: Create new feed
    print("=" * 60)
    print("Step 1: Creating new RSS feed with Episode 1")
    print("=" * 60)

    feed_xml = create_new_feed(podcast, ep1)
    print(f"Episodes in feed: {count_episodes(feed_xml)}")
    print(f"XML length: {len(feed_xml)} chars")
    print()

    # Episode 2
    ep2 = EpisodeAssets(
        script_id="scr_demo_002",
        title="AI Agents Are Replacing Workflows",
        description=(
            "Multi-agent systems are automating entire business processes. "
            "We explore how teams are building AI pipelines in 2026."
        ),
        audio_url="https://res.cloudinary.com/duxc6oeju/podcast_audio/ep2.mp3",
        cover_image_url="https://res.cloudinary.com/duxc6oeju/covers/ep2.jpg",
        duration_seconds=980,
        tags=["ai", "agents", "automation"],
    )

    # Step 2: Add episode to existing feed
    print("=" * 60)
    print("Step 2: Adding Episode 2 to existing feed")
    print("=" * 60)

    updated_xml = add_episode_to_existing_feed(feed_xml, ep2)
    print(f"Episodes in feed: {count_episodes(updated_xml)}")
    print(f"XML length: {len(updated_xml)} chars")
    print()

    # Step 3: Show the feed
    print("=" * 60)
    print("Generated RSS Feed:")
    print("=" * 60)
    print(updated_xml)
    print()

    print("=" * 60)
    print("Next steps for the user:")
    print("  1. Feed is uploaded to Cloudinary (done by PublishingAgent)")
    print("  2. Copy the feed URL")
    print("  3. Submit it once to:")
    print("     - Spotify:        https://podcasters.spotify.com")
    print("     - Anghami:        https://anghami.com/podcasters")
    print("     - Apple Podcasts: https://podcastsconnect.apple.com")
    print("     - YouTube Music:  https://music.youtube.com/podcasts")
    print("  4. Every new episode auto-appears on all platforms")
    print("=" * 60)


if __name__ == "__main__":
    main()
