"""
Quick-start example showing how to use the Critic Agent (v1.2).

Usage:
    export GROQ_API_KEY=your_key_here
    python examples/quickstart.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas.models import (
    CriticInput,
    Script,
    ScriptTurn,
    VoiceMetadata,
    SourceMeta,
    EvaluationConfig,
)
from critic_agent import CriticAgent
from llm_clients import GroqLLMClient


def main():
    # 1. Build the input
    critic_input = CriticInput(
        script=Script(
            script_id="scr_demo_001",
            version=1,
            turns=[
                ScriptTurn(
                    speaker="host",
                    text="Welcome back to the show, everyone! Today we're diving into foldable phones. I've got our resident gadget nerd with me. So — Galaxy Z Fold 7. Worth the hype?",
                ),
                ScriptTurn(
                    speaker="guest",
                    text="Honestly? Yeah. Samsung dropped it in March 2026 and the hinge is way better than last year's.",
                ),
                ScriptTurn(
                    speaker="host",
                    text="Wait, the hinge was the big complaint though, right? Is this real or marketing?",
                ),
                ScriptTurn(
                    speaker="guest",
                    text="Real. The crease is actually less visible. And get this — the foldable market grew 23% year over year.",
                ),
            ],
        ),
        key_points=[
            "Samsung released the Galaxy Z Fold 7 in March 2026",
            "The redesigned hinge addresses prior durability concerns",
            "The crease on the screen is less visible than previous generations",
            "The foldable phone market grew 23% year over year",
        ],
        source_meta=SourceMeta(
            source_id="src_blog_xyz",
            type="blog",
            title="The Rise of Foldable Phones in 2026",
        ),
        voice_metadata=VoiceMetadata(
            voice_id="11labs_tech_bro_001",
            name="Jake",
            accent="American",
            tone_label="casual, energetic",
            language="en",
        ),
        evaluation_config=EvaluationConfig(
            attempt_number=1,
            max_attempts=3,
        ),
    )

    # 2. Initialize the agent (requires GROQ_API_KEY env var)
    agent = CriticAgent(llm_client=GroqLLMClient())

    # 3. Run evaluation
    result = agent.evaluate(critic_input)

    # 4. Inspect the result
    print(f"\n{'=' * 60}")
    print(f"Verdict: {result.verdict.value}")
    print(f"Passed: {result.passed}")
    print(f"Hard fail (hallucination): {result.hard_fail_triggered}")
    print(f"Weighted average: {result.weighted_average}")
    print(f"\nScores:")
    print(f"  Naturalness & Tone Match: {result.scores.naturalness_and_tone_match}/5")
    print(f"  Factual Grounding:        {result.scores.factual_grounding}/5")
    print(f"  Structural Coherence:     {result.scores.structural_coherence}/5")
    print(f"  Engagement:               {result.scores.engagement}/5")

    if result.failed_dimensions:
        print(f"\nFailed dimensions: {', '.join(result.failed_dimensions)}")
        print("\nFeedback for Generator:")
        for dim, fb in result.feedback.items():
            print(f"\n  [{dim}]")
            print(f"    Issue:    {fb.issue}")
            print(f"    Location: {fb.location}")
            print(f"    Fix:      {fb.fix}")

    if result.strengths:
        print(f"\nStrengths to preserve:")
        for s in result.strengths:
            print(f"  • {s}")

    print(f"\nLatency: {result.metadata.evaluation_time_ms}ms")
    print(f"Tokens used: {result.metadata.tokens_used}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
