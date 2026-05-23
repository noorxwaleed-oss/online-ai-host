"""
Unit tests for the Publishing Agent — v3.0 (RSS-based).

Tests the RSS feed generation and update logic.
Cloudinary upload is not tested (requires credentials).

Run with: cd publishing_agent && python test_publishing.py
"""

import sys
from datetime import datetime, timezone

from pub_models import (
    PublishingInput,
    EpisodeAssets,
    PodcastInfo,
)
from rss_builder import (
    create_new_feed,
    add_episode_to_existing_feed,
    count_episodes,
)


# ---------- FIXTURES ----------

def make_podcast() -> PodcastInfo:
    return PodcastInfo(
        podcast_title="AI Host Interview",
        podcast_description="AI-generated podcast interviews on trending topics.",
        author="Online AI Host Team",
        language="ar",
        category="Technology",
        cover_image_url="https://res.cloudinary.com/test/covers/podcast_cover.jpg",
    )


def make_episode(script_id: str = "scr_001", title: str = "Episode 1: Foldable Phones") -> EpisodeAssets:
    return EpisodeAssets(
        script_id=script_id,
        title=title,
        description="We discuss the Galaxy Z Fold 7 and the foldable market growth.",
        audio_url="https://res.cloudinary.com/test/podcast_audio/episode1.mp3",
        cover_image_url="https://res.cloudinary.com/test/covers/ep1_cover.jpg",
        duration_seconds=1245,
        tags=["tech", "smartphones", "samsung"],
    )


# ---------- RSS BUILDER TESTS ----------

def test_create_new_feed_produces_valid_xml():
    podcast = make_podcast()
    episode = make_episode()
    xml = create_new_feed(podcast, episode)

    assert '<rss' in xml
    assert 'version="2.0"' in xml
    assert "<channel>" in xml
    assert "<item>" in xml


def test_new_feed_contains_podcast_metadata():
    podcast = make_podcast()
    episode = make_episode()
    xml = create_new_feed(podcast, episode)

    assert podcast.podcast_title in xml
    assert podcast.podcast_description in xml
    assert podcast.author in xml
    assert podcast.language in xml
    assert podcast.cover_image_url in xml


def test_new_feed_contains_episode():
    podcast = make_podcast()
    episode = make_episode()
    xml = create_new_feed(podcast, episode)

    assert episode.title in xml
    assert episode.audio_url in xml
    assert episode.script_id in xml
    assert "audio/mpeg" in xml


def test_new_feed_has_one_episode():
    podcast = make_podcast()
    episode = make_episode()
    xml = create_new_feed(podcast, episode)

    assert count_episodes(xml) == 1


def test_add_episode_to_existing_feed():
    podcast = make_podcast()
    ep1 = make_episode("scr_001", "Episode 1")
    xml = create_new_feed(podcast, ep1)

    ep2 = make_episode("scr_002", "Episode 2")
    updated_xml = add_episode_to_existing_feed(xml, ep2)

    assert count_episodes(updated_xml) == 2
    assert "Episode 1" in updated_xml
    assert "Episode 2" in updated_xml


def test_new_episode_is_first_in_feed():
    """Newest episode should appear before older ones."""
    podcast = make_podcast()
    ep1 = make_episode("scr_001", "Episode 1")
    xml = create_new_feed(podcast, ep1)

    ep2 = make_episode("scr_002", "Episode 2")
    updated_xml = add_episode_to_existing_feed(xml, ep2)

    pos_ep2 = updated_xml.index("Episode 2")
    pos_ep1 = updated_xml.index("Episode 1")
    assert pos_ep2 < pos_ep1, "Newest episode should appear first in feed"


def test_episode_duration_format():
    episode = make_episode()
    episode.duration_seconds = 3661  # 1h 1m 1s
    podcast = make_podcast()
    xml = create_new_feed(podcast, episode)

    assert "01:01:01" in xml


def test_episode_tags_in_keywords():
    podcast = make_podcast()
    episode = make_episode()
    xml = create_new_feed(podcast, episode)

    assert "tech, smartphones, samsung" in xml


def test_multiple_episodes_accumulate():
    podcast = make_podcast()
    xml = create_new_feed(podcast, make_episode("scr_001", "Ep 1"))

    for i in range(2, 6):
        xml = add_episode_to_existing_feed(xml, make_episode(f"scr_{i:03d}", f"Ep {i}"))

    assert count_episodes(xml) == 5


# ---------- MODEL VALIDATION TESTS ----------

def test_episode_title_required():
    from pydantic import ValidationError
    try:
        EpisodeAssets(
            script_id="x",
            title="",
            description="Valid description here.",
            audio_url="https://example.com/audio.mp3",
            cover_image_url="https://example.com/cover.jpg",
        )
        assert False, "Should have raised ValidationError for empty title"
    except ValidationError:
        pass


def test_publishing_input_requires_episode():
    from pydantic import ValidationError
    try:
        PublishingInput(
            episode=None,
            podcast=make_podcast(),
        )
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass


if __name__ == "__main__":
    import traceback
    tests = [
        test_create_new_feed_produces_valid_xml,
        test_new_feed_contains_podcast_metadata,
        test_new_feed_contains_episode,
        test_new_feed_has_one_episode,
        test_add_episode_to_existing_feed,
        test_new_episode_is_first_in_feed,
        test_episode_duration_format,
        test_episode_tags_in_keywords,
        test_multiple_episodes_accumulate,
        test_episode_title_required,
        test_publishing_input_requires_episode,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"✓ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
