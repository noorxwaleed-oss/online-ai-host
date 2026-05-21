"""
Quick-start example for the Publishing Agent.

Demonstrates:
1. Building a PublishingInput from approved assets + user context
2. Calling the agent
3. Inspecting the per-platform results

Usage:
    python examples/quickstart.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas.models import (
    PublishingInput,
    PublishableAssets,
    UserContext,
    Platform,
)
from publishing_agent import PublishingAgent
from adapters.mock_adapters import MOCK_CONNECTIONS


def main():
    # In real usage, audio_file_path and cover_image_path would point to
    # files produced by Aya's Audio Production Agent and Nour's Cover Design
    # Agent. For this demo we create temp files.
    audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    audio.write(b"fake mp3 bytes - in production this is the real episode")
    audio.close()

    cover = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    cover.write(b"fake jpg bytes - in production this is the cover art")
    cover.close()

    # 1. Build the input
    publishing_input = PublishingInput(
        assets=PublishableAssets(
            script_id="scr_demo_001",
            title="The Rise of Foldable Phones in 2026",
            description=(
                "Samsung's Galaxy Z Fold 7 is here — and it might finally "
                "make foldables mainstream. We dig into the redesigned hinge, "
                "the 23% YoY market growth, and whether the price tag is "
                "justified. With our resident tech reviewer."
            ),
            audio_file_path=audio.name,
            cover_image_path=cover.name,
            tags=["tech", "smartphones", "samsung"],
            duration_seconds=1245,
        ),
        user=UserContext(
            user_id="demo_user",
            connected_platforms=list(MOCK_CONNECTIONS["demo_user"]),
        ),
        target_platforms=[
            Platform.BUZZSPROUT,
            Platform.LINKEDIN,
            Platform.TWITTER,
            Platform.INSTAGRAM,
        ],
    )

    # 2. Run the agent
    agent = PublishingAgent()
    result = agent.publish(publishing_input)

    # 3. Inspect the result
    print(f"\n{'=' * 60}")
    print(f"Script ID:        {result.script_id}")
    print(f"Overall Status:   {result.overall_status.value}")
    print(f"Succeeded:        {result.total_succeeded}")
    print(f"Failed:           {result.total_failed}")
    print(f"Skipped:          {result.total_skipped}")
    print(f"{'=' * 60}\n")

    print("Per-platform results:\n")
    for r in result.results:
        marker = {
            "SUCCESS": "✓",
            "FAILED": "✗",
            "SKIPPED_NOT_CONNECTED": "—",
        }.get(r.status.value, "?")
        print(f"  {marker} {r.platform.value.upper():<12} {r.status.value}")
        if r.published_url:
            print(f"      URL:        {r.published_url}")
            print(f"      Post ID:    {r.platform_post_id}")
            print(f"      Latency:    {r.latency_ms}ms")
        if r.error_message:
            print(f"      Error:      {r.error_message}")
        print()

    print(f"Audit log: {Path(__file__).parent.parent / 'audit_log.jsonl'}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
