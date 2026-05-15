"""
Unit tests for the Publishing Agent.

These tests use the mock adapters and write to a real audit log file
(because the audit log is part of what we're verifying works). The audit
log is cleared at the start of each test session.

Run with: cd publishing_agent && python tests/test_publishing.py
"""

import sys
import tempfile
from pathlib import Path

from models import (
    PublishingInput,
    PublishableAssets,
    UserContext,
    Platform,
    PublishStatus,
)
from publishing_agent import PublishingAgent
from mock_adapters import MOCK_CONNECTIONS, AUDIT_LOG_PATH


# ---------- FIXTURES ----------

def make_temp_files() -> tuple[str, str]:
    """Create temporary audio + cover files so adapters' file checks pass."""
    audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    audio.write(b"fake mp3 bytes")
    audio.close()

    cover = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    cover.write(b"fake jpg bytes")
    cover.close()

    return audio.name, cover.name


def make_input(
    user_id: str = "demo_user",
    target_platforms: list[Platform] | None = None,
    audio_path: str | None = None,
    cover_path: str | None = None,
) -> PublishingInput:
    """Build a sample PublishingInput for testing."""
    if audio_path is None or cover_path is None:
        audio_path, cover_path = make_temp_files()

    return PublishingInput(
        assets=PublishableAssets(
            script_id="scr_test_001",
            title="Test Episode: The Future of AI",
            description=(
                "In this episode we discuss the rapidly evolving landscape "
                "of AI agents and what it means for software developers."
            ),
            audio_file_path=audio_path,
            cover_image_path=cover_path,
            tags=["ai", "tech", "agents"],
            duration_seconds=1800,
        ),
        user=UserContext(
            user_id=user_id,
            connected_platforms=list(MOCK_CONNECTIONS.get(user_id, set())),
        ),
        target_platforms=target_platforms or [Platform.SPOTIFY, Platform.ANGHAMI],
    )


def cleanup_audit_log():
    """Remove audit log between test runs for clean assertions."""
    if AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.unlink()


# ---------- TESTS ----------

def test_happy_path_two_platforms():
    """User has both platforms connected; both should succeed."""
    cleanup_audit_log()
    agent = PublishingAgent()
    out = agent.publish(make_input(target_platforms=[Platform.SPOTIFY, Platform.ANGHAMI]))

    assert out.overall_status == PublishStatus.SUCCESS
    assert out.total_succeeded == 2
    assert out.total_failed == 0
    assert out.total_skipped == 0
    assert len(out.results) == 2
    for r in out.results:
        assert r.status == PublishStatus.SUCCESS
        assert r.published_url is not None
        assert r.platform_post_id is not None
        assert r.latency_ms > 0


def test_all_four_platforms():
    """User has all four platforms; all should succeed."""
    cleanup_audit_log()
    agent = PublishingAgent()
    out = agent.publish(make_input(target_platforms=[
        Platform.SPOTIFY, Platform.ANGHAMI,
        Platform.YOUTUBE_MUSIC, Platform.APPLE_PODCASTS,
    ]))

    assert out.overall_status == PublishStatus.SUCCESS
    assert out.total_succeeded == 4
    assert out.total_failed == 0


def test_unconnected_platform_is_skipped():
    """User without Anghami linked should get SKIPPED_NOT_CONNECTED."""
    cleanup_audit_log()
    # Add a user with only Spotify linked
    MOCK_CONNECTIONS["partial_user"] = {Platform.SPOTIFY}

    agent = PublishingAgent()
    out = agent.publish(make_input(
        user_id="partial_user",
        target_platforms=[Platform.SPOTIFY, Platform.ANGHAMI],
    ))

    assert out.overall_status == PublishStatus.FAILED  # because something was skipped
    assert out.total_succeeded == 1
    assert out.total_skipped == 1
    assert out.total_failed == 0

    skipped_result = next(r for r in out.results if r.platform == Platform.ANGHAMI)
    assert skipped_result.status == PublishStatus.SKIPPED_NOT_CONNECTED
    assert "anghami" in skipped_result.error_message.lower()

    # Cleanup
    del MOCK_CONNECTIONS["partial_user"]


def test_missing_audio_file_fails_gracefully():
    """If the audio file doesn't exist, adapter returns FAILED, doesn't raise."""
    cleanup_audit_log()
    inp = make_input(audio_path="/nonexistent/file.mp3", cover_path=make_temp_files()[1])
    agent = PublishingAgent()
    out = agent.publish(inp)

    assert out.overall_status == PublishStatus.FAILED
    assert out.total_failed == len(inp.target_platforms)
    for r in out.results:
        assert r.status == PublishStatus.FAILED
        assert "not found" in r.error_message.lower()


def test_audit_log_records_publishes():
    """Each successful publish writes a line to the audit log."""
    cleanup_audit_log()
    agent = PublishingAgent()
    agent.publish(make_input(target_platforms=[Platform.SPOTIFY]))
    agent.publish(make_input(target_platforms=[Platform.ANGHAMI]))

    assert AUDIT_LOG_PATH.exists()
    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2

    import json
    record1 = json.loads(lines[0])
    record2 = json.loads(lines[1])
    assert record1["platform"] == "spotify"
    assert record2["platform"] == "anghami"
    assert "platform_post_id" in record1
    assert "url" in record1


def test_target_platforms_must_have_no_duplicates():
    """The schema rejects duplicate platforms in target_platforms."""
    from pydantic import ValidationError

    audio, cover = make_temp_files()
    try:
        PublishingInput(
            assets=PublishableAssets(
                script_id="x", title="t", description="description over ten chars",
                audio_file_path=audio, cover_image_path=cover,
            ),
            user=UserContext(user_id="demo_user"),
            target_platforms=[Platform.SPOTIFY, Platform.SPOTIFY],
        )
        assert False, "Should have raised ValidationError for duplicates"
    except ValidationError:
        pass  # Expected


def test_description_max_length_validated():
    """Schema rejects descriptions over 2000 chars."""
    from pydantic import ValidationError

    audio, cover = make_temp_files()
    long_description = "X" * 2500
    try:
        PublishableAssets(
            script_id="scr_long",
            title="Test",
            description=long_description,
            audio_file_path=audio,
            cover_image_path=cover,
        )
        assert False, "Should have raised ValidationError for long description"
    except ValidationError:
        pass  # Expected


def test_unique_post_ids_across_publishes():
    """Each publish should generate a unique post_id (UUIDs)."""
    cleanup_audit_log()
    agent = PublishingAgent()
    out1 = agent.publish(make_input(target_platforms=[Platform.SPOTIFY]))
    out2 = agent.publish(make_input(target_platforms=[Platform.SPOTIFY]))

    id1 = out1.results[0].platform_post_id
    id2 = out2.results[0].platform_post_id
    assert id1 != id2


def test_overall_status_is_success_only_when_all_succeed():
    """Strict success rule: any failure or skip → overall FAILED."""
    cleanup_audit_log()
    # Force a failure by using a bad path
    audio, cover = make_temp_files()
    inp = PublishingInput(
        assets=PublishableAssets(
            script_id="scr_mixed",
            title="Test",
            description="A reasonable description here.",
            audio_file_path="/does/not/exist.mp3",   # will fail
            cover_image_path=cover,
        ),
        user=UserContext(user_id="demo_user"),
        target_platforms=[Platform.SPOTIFY],
    )
    agent = PublishingAgent()
    out = agent.publish(inp)
    assert out.overall_status == PublishStatus.FAILED


if __name__ == "__main__":
    import traceback
    tests = [
        test_happy_path_two_platforms,
        test_all_four_platforms,
        test_unconnected_platform_is_skipped,
        test_missing_audio_file_fails_gracefully,
        test_audit_log_records_publishes,
        test_target_platforms_must_have_no_duplicates,
        test_description_max_length_validated,
        test_unique_post_ids_across_publishes,
        test_overall_status_is_success_only_when_all_succeed,
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
