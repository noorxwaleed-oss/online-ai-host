"""
Prompt construction for the Critic LLM call — v1.2.

Changes from v1.0:
- Uses voice_metadata (accent, tone_label, language) instead of persona_profile
- Uses key_points list directly for hallucination check
- Output schema reflects the 4-dimension scoring
"""

from models import CriticInput
from rubric import format_rubric_for_prompt


SYSTEM_PROMPT = """You are a strict but fair Quality Control critic for AI-generated podcast scripts.
Your job is to evaluate scripts across 4 dimensions and return ONLY valid JSON matching the required schema.

You are NOT here to rewrite the script. You only evaluate and give feedback.
Be specific. Cite turn numbers. Suggest concrete fixes."""


def build_user_prompt(inp: CriticInput) -> str:
    """Compose the per-call user message."""

    # Format the script with turn indices for precise feedback locations
    script_lines = []
    for i, turn in enumerate(inp.script.turns):
        script_lines.append(f"[turn {i}] {turn.speaker.upper()}: {turn.text}")
    formatted_script = "\n".join(script_lines)

    # Format the voice metadata
    voice = inp.voice_metadata
    voice_block = f"""Name: {voice.name}
Accent: {voice.accent}
Tone label: {voice.tone_label}
Language: {voice.language}
Voice ID: {voice.voice_id}"""

    # Format the key points as a numbered list
    key_points_block = "\n".join(
        f"  {i+1}. {kp}" for i, kp in enumerate(inp.key_points)
    )

    # Inject prior feedback if this is a revision attempt
    feedback_block = ""
    cfg = inp.evaluation_config
    if cfg.attempt_number > 1 and cfg.previous_feedback:
        feedback_block = f"""
## Previous Attempt Feedback
This is attempt {cfg.attempt_number} of {cfg.max_attempts}.
The script previously failed on: {", ".join(cfg.previous_feedback.failed_dimensions)}
Summary: {cfg.previous_feedback.summary}

Verify whether prior issues were fixed. Be especially attentive to those dimensions.
"""

    rubric_text = format_rubric_for_prompt()

    return f"""Evaluate the following podcast script.

# RUBRIC
{rubric_text}

# VOICE METADATA (the script's tone should match this voice)
{voice_block}

# KEY POINTS (the script must be factually grounded in these — any claim NOT in this list is a hallucination)
{key_points_block}

# SOURCE INFO
Title: {inp.source_meta.title}
Type: {inp.source_meta.type}

# SCRIPT TO EVALUATE
{formatted_script}
{feedback_block}

# YOUR TASK
1. Score each of the 4 dimensions on a 1-5 scale using the rubric above.
2. For ANY dimension scoring below the pass threshold, provide structured feedback with: issue, location (cite turn numbers), and a concrete fix.
3. List 1-3 strengths so the Generator preserves what worked.
4. Hard rule on factual_grounding: if the script contains ANY claim not supported by the key points list above, score it below 5.
5. Tone match: a "casual, energetic" voice should not be paired with formal/academic writing. Penalize mismatches under naturalness_and_tone_match.

# OUTPUT FORMAT
Return ONLY a JSON object with this exact shape (no markdown fences, no preamble):
{{
  "scores": {{
    "naturalness_and_tone_match": <int 1-5>,
    "factual_grounding": <int 1-5>,
    "structural_coherence": <int 1-5>,
    "engagement": <int 1-5>
  }},
  "feedback": {{
    "<dimension_name>": {{
      "issue": "<what is wrong>",
      "location": "<turn numbers, e.g., 'turns[3-6]'>",
      "fix": "<concrete suggestion>"
    }}
  }},
  "strengths": ["<strength 1>", "<strength 2>"]
}}

Only include `feedback` entries for dimensions that need improvement. If a dimension scores 5, do not include it in feedback."""
