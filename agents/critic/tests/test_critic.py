"""
Unit tests for the Critic Agent — v1.2.

Updated for:
- VoiceMetadata replaces PersonaProfile
- key_points is top-level
- 4 dimensions instead of 5

Run with: cd critic_agent_v12 && python tests/test_critic.py
"""

import json
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
    DimensionScores,
    Verdict,
)
from rubric import (
    compute_weighted_average,
    decide_verdict,
    find_failed_dimensions,
)
from critic_agent import CriticAgent
from llm_clients import MockLLMClient


# ---------- FIXTURES ----------

def make_input(attempt: int = 1) -> CriticInput:
    """Build a sample CriticInput for testing."""
    return CriticInput(
        script=Script(
            script_id="scr_test_001",
            version=1,
            turns=[
                ScriptTurn(speaker="host", text="Welcome to the show!"),
                ScriptTurn(speaker="guest", text="Thanks for having me."),
                ScriptTurn(speaker="host", text="Let's dig in. What got you started?"),
                ScriptTurn(speaker="guest", text="It started with unboxing my first phone."),
            ],
        ),
        key_points=[
            "Tech reviewers often start with unboxing experiences",
            "Modern smartphones are tested for various specifications",
        ],
        source_meta=SourceMeta(
            source_id="src_test",
            type="blog",
            title="Tech Trends",
        ),
        voice_metadata=VoiceMetadata(
            voice_id="11labs_test_voice",
            name="Tech Host",
            accent="American",
            tone_label="casual, energetic",
            language="en",
        ),
        evaluation_config=EvaluationConfig(
            attempt_number=attempt,
            max_attempts=3,
        ),
    )


# ---------- RUBRIC LOGIC TESTS ----------

def test_perfect_script_passes():
    scores = DimensionScores(
        naturalness_and_tone_match=5,
        factual_grounding=5,
        structural_coherence=5,
        engagement=5,
    )
    verdict, passed, hard_fail = decide_verdict(scores, attempt_number=1, max_attempts=3)
    assert verdict == Verdict.PASS
    assert passed is True
    assert hard_fail is False
    assert compute_weighted_average(scores) == 5.0


def test_hallucination_always_fails():
    scores = DimensionScores(
        naturalness_and_tone_match=5,
        factual_grounding=4,
        structural_coherence=5,
        engagement=5,
    )
    verdict, passed, hard_fail = decide_verdict(scores, attempt_number=1, max_attempts=3)
    assert hard_fail is True
    assert passed is False
    assert verdict == Verdict.REJECT


def test_hallucination_blocks_final_attempt_fallback():
    scores = DimensionScores(
        naturalness_and_tone_match=5,
        factual_grounding=2,
        structural_coherence=5,
        engagement=5,
    )
    verdict, passed, _ = decide_verdict(scores, attempt_number=3, max_attempts=3)
    assert verdict == Verdict.REJECT
    assert passed is False


def test_final_attempt_accepts_with_warning():
    """At max attempts, mediocre scripts (below 3.5 avg, no hallucination) get ACCEPT_WITH_WARNING."""
    # 3*0.30 + 5*0.25 + 2*0.20 + 3*0.25 = 0.9 + 1.25 + 0.4 + 0.75 = 3.30 (below 3.5 → not regular pass)
    scores = DimensionScores(
        naturalness_and_tone_match=3,
        factual_grounding=5,
        structural_coherence=2,
        engagement=3,
    )
    verdict, passed, _ = decide_verdict(scores, attempt_number=3, max_attempts=3)
    assert verdict == Verdict.ACCEPT_WITH_WARNING
    assert passed is True


def test_catastrophic_dimension_fails():
    scores = DimensionScores(
        naturalness_and_tone_match=1,
        factual_grounding=5,
        structural_coherence=5,
        engagement=5,
    )
    verdict, passed, _ = decide_verdict(scores, attempt_number=1, max_attempts=3)
    assert verdict == Verdict.REJECT
    assert passed is False


def test_borderline_passes_at_3_5():
    """Weighted avg with new weights: 4*0.30 + 5*0.25 + 3*0.20 + 3*0.25 = 3.80 — passes."""
    scores = DimensionScores(
        naturalness_and_tone_match=4,
        factual_grounding=5,
        structural_coherence=3,
        engagement=3,
    )
    verdict, passed, _ = decide_verdict(scores, attempt_number=1, max_attempts=3)
    assert passed is True
    assert verdict == Verdict.PASS


def test_failed_dimensions_listed_correctly():
    scores = DimensionScores(
        naturalness_and_tone_match=2,
        factual_grounding=5,
        structural_coherence=5,
        engagement=2,
    )
    failed = find_failed_dimensions(scores)
    assert "naturalness_and_tone_match" in failed
    assert "engagement" in failed
    assert "factual_grounding" not in failed


def test_weights_sum_to_one():
    from rubric import DIMENSION_WEIGHTS
    total = sum(DIMENSION_WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9, f"Weights must sum to 1.0, got {total}"


# ---------- AGENT INTEGRATION TESTS ----------

def test_agent_handles_perfect_response():
    mock_response = json.dumps({
        "scores": {
            "naturalness_and_tone_match": 5,
            "factual_grounding": 5,
            "structural_coherence": 5,
            "engagement": 5,
        },
        "feedback": {},
        "strengths": ["Excellent flow", "Tone matches voice"],
    })
    agent = CriticAgent(llm_client=MockLLMClient(canned_response=mock_response))
    result = agent.evaluate(make_input())

    assert result.verdict == Verdict.PASS
    assert result.passed is True
    assert result.hard_fail_triggered is False
    assert result.scores.naturalness_and_tone_match == 5
    assert len(result.strengths) == 2


def test_agent_handles_response_with_markdown_fences():
    mock_response = """```json
{
  "scores": {
    "naturalness_and_tone_match": 4,
    "factual_grounding": 5,
    "structural_coherence": 4,
    "engagement": 4
  },
  "feedback": {},
  "strengths": ["Good"]
}
```"""
    agent = CriticAgent(llm_client=MockLLMClient(canned_response=mock_response))
    result = agent.evaluate(make_input())
    assert result.passed is True


def test_agent_returns_structured_feedback_on_failure():
    mock_response = json.dumps({
        "scores": {
            "naturalness_and_tone_match": 2,
            "factual_grounding": 5,
            "structural_coherence": 3,
            "engagement": 3,
        },
        "feedback": {
            "naturalness_and_tone_match": {
                "issue": "Tone is academic but voice is casual/energetic",
                "location": "turns[3-6]",
                "fix": "Replace formal connectors with casual ones (so, yeah, right)",
            }
        },
        "strengths": ["All factual claims trace to key_points"],
    })
    agent = CriticAgent(llm_client=MockLLMClient(canned_response=mock_response))
    result = agent.evaluate(make_input())

    assert result.passed is False
    assert result.verdict == Verdict.REJECT
    assert "naturalness_and_tone_match" in result.feedback
    assert result.feedback["naturalness_and_tone_match"].location == "turns[3-6]"


def test_agent_metadata_is_populated():
    mock_response = json.dumps({
        "scores": {
            "naturalness_and_tone_match": 5, "factual_grounding": 5,
            "structural_coherence": 5, "engagement": 5,
        },
        "feedback": {},
        "strengths": [],
    })
    agent = CriticAgent(llm_client=MockLLMClient(canned_response=mock_response))
    result = agent.evaluate(make_input())

    assert result.metadata.evaluator_model == "mock-llm-v1"
    assert result.metadata.evaluation_time_ms >= 0
    assert result.metadata.timestamp is not None


def test_v12_input_validates_voice_metadata():
    """Verify the new VoiceMetadata field is required and validates."""
    inp = make_input()
    assert inp.voice_metadata.accent == "American"
    assert inp.voice_metadata.language == "en"
    assert inp.key_points  # Top-level field, not nested


if __name__ == "__main__":
    import traceback
    tests = [
        test_perfect_script_passes,
        test_hallucination_always_fails,
        test_hallucination_blocks_final_attempt_fallback,
        test_final_attempt_accepts_with_warning,
        test_catastrophic_dimension_fails,
        test_borderline_passes_at_3_5,
        test_failed_dimensions_listed_correctly,
        test_weights_sum_to_one,
        test_agent_handles_perfect_response,
        test_agent_handles_response_with_markdown_fences,
        test_agent_returns_structured_feedback_on_failure,
        test_agent_metadata_is_populated,
        test_v12_input_validates_voice_metadata,
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
