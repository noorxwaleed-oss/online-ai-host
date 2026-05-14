"""
Integration entry point for the Critic Agent.

This file is the contract surface that Asmaa's orchestrator imports from:

    from agents.critic.agent import evaluate_script
    critique = await evaluate_script(payload_dict)

The wrapper translates between two worlds:
  - The orchestrator speaks dicts (LangGraph state is dicts)
  - The Critic internals speak Pydantic objects (CriticInput / CriticOutput)

It also fixes the import path so the Critic's internal modules
(`schemas`, `rubric`, etc.) resolve correctly when called from the
project root rather than from within agents/critic/.
"""

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------
# Your internal Critic code uses imports like `from schemas.models import ...`
# which assume `agents/critic/` is on sys.path. When Asmaa's orchestrator
# runs from the project root, that's not the case. So we add it here.
#
# This makes the wrapper portable: it works whether the orchestrator
# is run from the project root, from within agents/critic/, or anywhere else.
_CRITIC_DIR = Path(__file__).parent.resolve()
if str(_CRITIC_DIR) not in sys.path:
    sys.path.insert(0, str(_CRITIC_DIR))

# ---------------------------------------------------------------
# Imports from the Critic's internal code
# ---------------------------------------------------------------
# These work because we just added _CRITIC_DIR to sys.path above.
from schemas.models import CriticInput  # noqa: E402
from critic_agent import CriticAgent     # noqa: E402
from llm_clients import GroqLLMClient    # noqa: E402

# ---------------------------------------------------------------
# Singleton agent
# ---------------------------------------------------------------
# We initialize the CriticAgent once, when this module is first imported,
# and reuse it across every request. Two reasons:
#   1. The Groq client opens an HTTP connection pool — wasteful to recreate
#   2. The agent has no per-request state (it's deterministic logic), so
#      sharing it across requests is safe
#
# If GROQ_API_KEY is missing, this will raise on import. That's intentional —
# we want failures to be loud and early, not silent at first call time.
_agent: CriticAgent | None = None


def _get_agent() -> CriticAgent:
    """Lazy initialization so import doesn't fail in environments without
    GROQ_API_KEY (e.g., when teammates clone the repo without setting up
    their .env yet). The agent is built on first actual call to evaluate_script."""
    global _agent
    if _agent is None:
        _agent = CriticAgent(llm_client=GroqLLMClient())
    return _agent


# ---------------------------------------------------------------
# The integration contract
# ---------------------------------------------------------------

async def evaluate_script(payload: dict) -> dict:
    """
    Public entry point. Asmaa's orchestrator calls this.

    Input shape (dict matching CriticInput):
        {
            "script": {
                "script_id": str,
                "version": int,
                "turns": [{"speaker": "host"|"guest", "text": str}, ...]
            },
            "key_points": [str, ...],
            "source_meta": {"source_id": str, "type": str, "title": str},
            "voice_metadata": {
                "voice_id": str, "name": str, "accent": str,
                "tone_label": str, "language": str
            },
            "evaluation_config": {
                "attempt_number": int,
                "max_attempts": int,
                "previous_feedback": None | {"failed_dimensions": [...], "summary": str}
            }
        }

    Output shape (dict matching CriticOutput):
        {
            "script_id": str,
            "version": int,
            "verdict": "PASS"|"REJECT"|"ACCEPT_WITH_WARNING",
            "passed": bool,
            "scores": {<dimension>: 1-5, ...},
            "weighted_average": float,
            "hard_fail_triggered": bool,
            "failed_dimensions": [str, ...],
            "feedback": {<dimension>: {"issue": str, "location": str, "fix": str}, ...},
            "strengths": [str, ...],
            "metadata": {"evaluator_model": str, ...}
        }

    Why `async` even though the underlying agent is sync:
        The orchestrator uses LangGraph + asyncio.gather() and expects coroutines.
        Marking this `async def` makes it awaitable. The internal LLM call is
        currently sync (Groq's Python SDK is sync), so this function returns
        almost immediately as a coroutine but the actual LLM work happens
        synchronously when awaited. That's fine — only noticeable difference
        is that this won't yield the event loop during the LLM call. For
        graduation scope this is acceptable; we can switch to an async client
        later if needed.
    """
    # Step 1: Validate the dict against our Pydantic schema.
    # If the orchestrator sends a malformed payload, this raises a clear
    # ValidationError pointing at the exact field that's wrong.
    critic_input = CriticInput(**payload)

    # Step 2: Run the actual evaluation.
    agent = _get_agent()
    result = agent.evaluate(critic_input)

    # Step 3: Convert the Pydantic output back to a dict for the orchestrator.
    # mode="json" ensures datetime fields are serialized as ISO strings,
    # which is what the orchestrator's state expects.
    return result.model_dump(mode="json")
