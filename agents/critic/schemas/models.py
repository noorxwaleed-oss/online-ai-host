"""
Data schemas for the Critic Agent — v1.2.

Changes from v1.0:
- Removed PersonaProfile (no Persona Agent in the pipeline)
- Added VoiceMetadata (matches what ElevenLabs/MiniMax expose)
- key_points is now a top-level field on CriticInput (extracted upstream by Nour's
  Text Extraction Agent), not a sub-field of source_content
- DimensionScores: dropped persona_consistency, renamed naturalness to
  naturalness_and_tone_match
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ---------- INPUT MODELS ----------

class ScriptTurn(BaseModel):
    """A single turn of dialogue in the script."""
    speaker: str = Field(..., description="Either 'host' or 'guest'")
    text: str = Field(..., min_length=1)

    @field_validator("speaker")
    @classmethod
    def validate_speaker(cls, v: str) -> str:
        if v not in ("host", "guest"):
            raise ValueError(f"speaker must be 'host' or 'guest', got '{v}'")
        return v


class Script(BaseModel):
    """The script being evaluated."""
    script_id: str
    version: int = Field(..., ge=1)
    turns: list[ScriptTurn] = Field(..., min_length=2)


class VoiceMetadata(BaseModel):
    """
    Voice context for the host (owned by Aya / ElevenLabs).
    Replaces the v1.0 PersonaProfile. The Critic uses this to check
    whether the script's tone matches the chosen voice.
    """
    voice_id: str = Field(..., description="ElevenLabs/MiniMax voice ID")
    name: str = Field(..., description="Display name (e.g., 'Salma')")
    accent: str = Field(..., description="e.g., 'American', 'British', 'Egyptian Arabic'")
    tone_label: str = Field(
        ...,
        description="Brief tone description, e.g., 'casual, energetic'"
    )
    language: str = Field(..., description="ISO code, e.g., 'en', 'ar'")


class SourceMeta(BaseModel):
    """Identifiers for the source. The Critic does NOT need raw source text."""
    source_id: str
    type: str = Field(..., description="'blog', 'video_transcript', 'article'")
    title: str


class PreviousFeedback(BaseModel):
    """Feedback from a prior attempt (None on attempt 1)."""
    failed_dimensions: list[str]
    summary: str


class EvaluationConfig(BaseModel):
    """Loop control info passed by the Orchestrator."""
    attempt_number: int = Field(..., ge=1, le=10)
    max_attempts: int = Field(default=3, ge=1, le=10)
    previous_feedback: Optional[PreviousFeedback] = None


class CriticInput(BaseModel):
    """
    The full input the Critic Agent accepts (v1.2).
    This is the contract. The Orchestrator MUST send this shape.
    """
    script: Script
    key_points: list[str] = Field(
        ...,
        min_length=1,
        description=(
            "Factual claims extracted by the Text Extraction Agent. "
            "Whitelist for the Critic's hallucination check."
        ),
    )
    source_meta: SourceMeta
    voice_metadata: VoiceMetadata
    evaluation_config: EvaluationConfig


# ---------- OUTPUT MODELS ----------

class Verdict(str, Enum):
    PASS = "PASS"
    REJECT = "REJECT"
    ACCEPT_WITH_WARNING = "ACCEPT_WITH_WARNING"  # Used at final attempt fallback


class DimensionScores(BaseModel):
    """1-5 score per dimension. 5 = best, 1 = worst. v1.2: 4 dimensions."""
    naturalness_and_tone_match: int = Field(..., ge=1, le=5)
    factual_grounding: int = Field(..., ge=1, le=5)
    structural_coherence: int = Field(..., ge=1, le=5)
    engagement: int = Field(..., ge=1, le=5)


class DimensionFeedback(BaseModel):
    """Structured feedback the Generator can act on directly."""
    issue: str = Field(..., description="What is wrong")
    location: str = Field(..., description="Where in the script (e.g., 'turns[3-6]')")
    fix: str = Field(..., description="Concrete suggestion to repair it")


class CriticMetadata(BaseModel):
    """Logged for MLflow tracking in Milestone 4."""
    evaluator_model: str
    evaluation_time_ms: int
    tokens_used: int
    timestamp: datetime


class CriticOutput(BaseModel):
    """The full output the Critic Agent returns."""
    script_id: str
    version: int
    verdict: Verdict
    passed: bool
    scores: DimensionScores
    weighted_average: float = Field(..., ge=1.0, le=5.0)
    hard_fail_triggered: bool = Field(
        ...,
        description="True if factual_grounding < 5 (zero tolerance for hallucination)"
    )
    failed_dimensions: list[str]
    feedback: dict[str, DimensionFeedback]
    strengths: list[str] = Field(default_factory=list)
    metadata: CriticMetadata
