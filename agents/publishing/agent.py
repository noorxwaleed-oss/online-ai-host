"""
Integration entry point for the Publishing Agent.

Note: Publishing is NOT in the current LangGraph workflow. It's called
separately when the user clicks "Publish" on the frontend after reviewing
the generated assets. The orchestrator (or a future /publish FastAPI
endpoint) will import this function:

    from agents.publishing.agent import publish_to_platforms
    result = await publish_to_platforms(payload_dict)

The wrapper translates between dict (the integration boundary) and
Pydantic objects (the internal world). Same pattern as agents/critic/agent.py.
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------
# Internal Publishing code uses imports like `from schemas.models import ...`
# which assume agents/publishing/ is on sys.path. When the orchestrator runs
# from the project root, that's not the case. So we add it here.
_PUBLISHING_DIR = Path(__file__).parent.resolve()
if str(_PUBLISHING_DIR) not in sys.path:
    sys.path.insert(0, str(_PUBLISHING_DIR))

# ---------------------------------------------------------------
# Imports from the Publishing internal code
# ---------------------------------------------------------------
from schemas.models import PublishingInput  # noqa: E402
from publishing_agent import PublishingAgent  # noqa: E402

# ---------------------------------------------------------------
# Singleton agent
# ---------------------------------------------------------------
# PublishingAgent has no expensive dependencies (mock adapters are cheap),
# but we still cache it for consistency with the Critic pattern.
_agent: PublishingAgent | None = None


def _get_agent() -> PublishingAgent:
    """Lazy initialization. The agent has no API key requirements
    (all adapters are mocked), so this works in any environment."""
    global _agent
    if _agent is None:
        _agent = PublishingAgent()
    return _agent


# ---------------------------------------------------------------
# Public integration contract
# ---------------------------------------------------------------

async def publish_to_platforms(payload: dict) -> dict:
    """
    Public entry point. Called when the user triggers publishing.

    Input shape (dict matching PublishingInput):
        {
            "assets": {
                "script_id": str,
                "title": str,
                "description": str,
                "audio_file_path": str,
                "cover_image_path": str,
                "transcript": str | None,
                "tags": [str, ...],
                "duration_seconds": int | None
            },
            "user": {
                "user_id": str,
                "connected_platforms": ["buzzsprout"|"linkedin"|"twitter"|"instagram", ...]
            },
            "target_platforms": ["buzzsprout"|"linkedin"|"twitter"|"instagram", ...]
        }

    Output shape (dict matching PublishingOutput):
        {
            "script_id": str,
            "overall_status": "SUCCESS"|"FAILED",
            "total_succeeded": int,
            "total_failed": int,
            "total_skipped": int,
            "results": [
                {
                    "platform": str,
                    "status": "SUCCESS"|"FAILED"|"SKIPPED_NOT_CONNECTED",
                    "published_url": str | None,
                    "platform_post_id": str | None,
                    "error_message": str | None,
                    "published_at": str | None,
                    "latency_ms": int
                },
                ...
            ],
            "timestamp": str
        }

    Why `async` even though the underlying agent is sync:
        The current adapters are mocked and synchronous, but in production
        each adapter would make real HTTP calls. Async-from-day-one means
        we won't have to change the contract when real adapters land.
    """
    # Step 1: Validate the dict against our Pydantic schema.
    publishing_input = PublishingInput(**payload)

    # Step 2: Run the publishing flow.
    agent = _get_agent()
    result = agent.publish(publishing_input)

    # Step 3: Convert the Pydantic output back to a dict for the caller.
    return result.model_dump(mode="json")
