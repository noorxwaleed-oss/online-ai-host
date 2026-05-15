"""
MLflow integration for the Critic Agent — Milestone 4.

Logs every evaluation as an MLflow run, capturing:
  - Parameters: model name, attempt number, language, topic
  - Metrics: per-dimension scores, weighted average, latency, tokens
  - Tags: verdict, hard_fail status, case_id

Why MLflow matters for this project:
  - Tracks Critic quality over time as you iterate on prompts/rubrics
  - Lets you compare runs side-by-side (e.g., "did v1.2 prompt beat v1.1?")
  - Required by Milestone 4's "MLOps Integration" deliverable

Usage:
    from mlflow_logger import log_critic_run

    output = critic.evaluate(input)
    log_critic_run(input, output, extra_tags={"case_id": "golden_001"})

If MLflow isn't installed or configured, logging silently no-ops so the
Critic can still run in environments without MLflow (e.g., a deploy server).
"""

import os
from typing import Optional

from models import CriticInput, CriticOutput


def log_critic_run(
    inp: CriticInput,
    out: CriticOutput,
    experiment_name: str = "critic_agent_evaluation",
    run_name: Optional[str] = None,
    extra_tags: Optional[dict] = None,
) -> Optional[str]:
    """
    Log a single Critic evaluation to MLflow.

    Returns the MLflow run_id if logged, None if MLflow is unavailable
    (e.g., not installed, MLFLOW_TRACKING_URI not set, etc.).
    """
    try:
        import mlflow
    except ImportError:
        # MLflow not installed — silently skip
        return None

    # Set tracking URI if env var provided, otherwise use default local ./mlruns
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    try:
        mlflow.set_experiment(experiment_name)
    except Exception:
        # Experiment creation may fail on remote servers without permissions
        return None

    if run_name is None:
        run_name = f"{inp.script.script_id}_v{inp.script.version}"

    with mlflow.start_run(run_name=run_name) as run:
        # ---- Parameters (immutable inputs) ----
        mlflow.log_params({
            "model": out.metadata.evaluator_model,
            "language": inp.voice_metadata.language,
            "voice_accent": inp.voice_metadata.accent,
            "tone_label": inp.voice_metadata.tone_label,
            "source_type": inp.source_meta.type,
            "attempt_number": inp.evaluation_config.attempt_number,
            "max_attempts": inp.evaluation_config.max_attempts,
            "num_turns": len(inp.script.turns),
            "num_key_points": len(inp.key_points),
        })

        # ---- Metrics (numerical) ----
        mlflow.log_metrics({
            "score_naturalness_and_tone_match": out.scores.naturalness_and_tone_match,
            "score_factual_grounding": out.scores.factual_grounding,
            "score_structural_coherence": out.scores.structural_coherence,
            "score_engagement": out.scores.engagement,
            "weighted_average": out.weighted_average,
            "evaluation_time_ms": out.metadata.evaluation_time_ms,
            "tokens_used": out.metadata.tokens_used,
            "passed_int": 1 if out.passed else 0,  # MLflow metrics are numeric
            "hard_fail_int": 1 if out.hard_fail_triggered else 0,
        })

        # ---- Tags (categorical / queryable) ----
        tags = {
            "verdict": out.verdict.value,
            "passed": str(out.passed),
            "hard_fail_triggered": str(out.hard_fail_triggered),
            "script_id": inp.script.script_id,
            "source_id": inp.source_meta.source_id,
            "voice_id": inp.voice_metadata.voice_id,
            "num_failed_dimensions": str(len(out.failed_dimensions)),
        }
        if extra_tags:
            tags.update({k: str(v) for k, v in extra_tags.items()})
        mlflow.set_tags(tags)

        return run.info.run_id


def log_golden_set_run(
    metrics: dict,
    results: list[dict],
    mode: str,
    experiment_name: str = "critic_agent_golden_set_runs",
) -> Optional[str]:
    """
    Log an entire golden-set evaluation as a single parent run.
    Useful for comparing Critic versions over time.
    """
    try:
        import mlflow
    except ImportError:
        return None

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    try:
        mlflow.set_experiment(experiment_name)
    except Exception:
        return None

    with mlflow.start_run(run_name=f"golden_set_{mode}") as run:
        mlflow.log_params({
            "mode": mode,
            "total_cases": metrics["total_cases"],
            "non_borderline_evaluated": metrics["non_borderline_evaluated"],
        })
        mlflow.log_metrics({
            "agreement_rate": metrics["agreement_rate"],
            "agreements": metrics["agreements"],
            "disagreements": metrics["disagreements"],
            "errored": metrics["errored"],
            "avg_latency_ms": metrics["avg_latency_ms"],
            "total_tokens_used": metrics["total_tokens_used"],
        })
        # Log each case as a metric step
        for i, r in enumerate(results):
            if r.get("error") is None:
                mlflow.log_metric("case_agrees", 1 if r.get("agrees") else 0, step=i)

        mlflow.set_tags({
            "mode": mode,
            "disagreement_case_ids": ",".join(metrics["disagreement_case_ids"]),
        })
        return run.info.run_id
