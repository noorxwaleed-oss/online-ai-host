"""
Rubric and pass/fail logic for the Critic Agent — v1.2.

Changes from v1.0:
- Removed persona_consistency dimension
- Renamed naturalness to naturalness_and_tone_match
- Reweighted: naturalness=0.30, factual=0.25, structural=0.20, engagement=0.25
"""

from models import DimensionScores, Verdict


# ---------- RUBRIC DESCRIPTIONS ----------

RUBRIC = {
    "naturalness_and_tone_match": {
        "description": (
            "Does it sound like two humans talking, AND does the script's tone "
            "match the chosen voice's accent/tone label? E.g., a 'casual, energetic' "
            "voice should not be paired with academic, formal writing."
        ),
        "levels": {
            5: "Indistinguishable from a real podcast; flows with reactions and natural interruptions; tone fully matches the voice's accent/tone label",
            4: "Mostly conversational and on-tone, with minor stiff or off-tone moments",
            3: "Readable as dialogue but feels scripted; or noticeable tone mismatch with the voice",
            2: "Reads like an article split into two voices, OR major tone mismatch (formal voice on casual topic, etc.)",
            1: "Robotic; clearly AI-generated essay format; no attempt to match voice tone",
        },
    },
    "factual_grounding": {
        "description": (
            "Every factual claim must trace back to the provided key_points. "
            "Zero tolerance for invented facts."
        ),
        "levels": {
            5: "Every factual claim is supported by key_points. No hallucinations.",
            4: "All facts grounded but minor unsupported elaborations exist",
            3: "Mostly grounded but contains 1-2 unsupported claims",
            2: "Several invented facts, statistics, or quotes",
            1: "Significant fabrication; script contradicts or invents content",
        },
    },
    "structural_coherence": {
        "description": "Does the interview have a logical arc?",
        "levels": {
            5: "Clear intro, logical progression, smooth transitions, proper closing",
            4: "Strong structure with minor transition issues",
            3: "Recognizable structure but uneven flow",
            2: "Topics jump around; weak intro or closing",
            1: "No clear structure",
        },
    },
    "engagement": {
        "description": "Would a listener actually want to keep listening?",
        "levels": {
            5: "Strong hook, specific examples, varied question types throughout",
            4: "Engaging with minor monotonous stretches",
            3: "Adequate engagement; some Q-A monotony",
            2: "Mostly flat; few examples or stories",
            1: "Boring; pure abstract back-and-forth",
        },
    },
}


# ---------- WEIGHTING ----------
# v1.2: 4 dimensions, sum = 1.0

DIMENSION_WEIGHTS = {
    "naturalness_and_tone_match": 0.30,
    "factual_grounding": 0.25,  # Hard-gated separately at score=5
    "structural_coherence": 0.20,
    "engagement": 0.25,
}


# ---------- PASS/FAIL LOGIC ----------

def compute_weighted_average(scores: DimensionScores) -> float:
    """Weighted average across all 4 dimensions."""
    return round(
        scores.naturalness_and_tone_match * DIMENSION_WEIGHTS["naturalness_and_tone_match"]
        + scores.factual_grounding * DIMENSION_WEIGHTS["factual_grounding"]
        + scores.structural_coherence * DIMENSION_WEIGHTS["structural_coherence"]
        + scores.engagement * DIMENSION_WEIGHTS["engagement"],
        2,
    )


def find_failed_dimensions(scores: DimensionScores) -> list[str]:
    """A dimension 'fails' if it scores below acceptable. Used for feedback targeting."""
    failed = []
    if scores.factual_grounding < 5:
        failed.append("factual_grounding")
    if scores.naturalness_and_tone_match < 4:
        failed.append("naturalness_and_tone_match")
    if scores.structural_coherence < 3:
        failed.append("structural_coherence")
    if scores.engagement < 3:
        failed.append("engagement")
    return failed


def decide_verdict(
    scores: DimensionScores,
    attempt_number: int,
    max_attempts: int,
) -> tuple[Verdict, bool, bool]:
    """
    Hybrid pass/fail rule:
      PASS if:
        factual_grounding == 5 (hard gate)
        AND weighted_average >= 3.5
        AND no other dimension scored below 2

    Returns: (verdict, passed, hard_fail_triggered)
    """
    hard_fail = scores.factual_grounding < 5
    weighted_avg = compute_weighted_average(scores)

    catastrophic = any(
        getattr(scores, dim) < 2
        for dim in [
            "naturalness_and_tone_match",
            "structural_coherence",
            "engagement",
        ]
    )

    is_pass = (not hard_fail) and (weighted_avg >= 3.5) and (not catastrophic)

    if is_pass:
        return Verdict.PASS, True, hard_fail

    if attempt_number >= max_attempts and not hard_fail:
        return Verdict.ACCEPT_WITH_WARNING, True, hard_fail

    return Verdict.REJECT, False, hard_fail


def format_rubric_for_prompt() -> str:
    """Render the rubric as a string the LLM can read."""
    lines = []
    for dim, info in RUBRIC.items():
        lines.append(f"\n## {dim.upper()}")
        lines.append(f"Definition: {info['description']}")
        lines.append("Levels:")
        for score in sorted(info["levels"].keys(), reverse=True):
            lines.append(f"  {score} = {info['levels'][score]}")
    return "\n".join(lines)
