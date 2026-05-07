"""
Golden Set Evaluation Runner.

Runs every case in the golden set through the Critic and measures
agreement with the human-labeled expected verdict.

Usage:
    # With a real LLM (requires GROQ_API_KEY):
    python evaluation/run_golden_set.py --live

    # With a mock LLM (for offline testing / CI):
    python evaluation/run_golden_set.py --mock

Outputs:
- results/run_<timestamp>.json — full results for every case
- results/run_<timestamp>.md — human-readable summary report
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas.models import CriticInput
from critic_agent import CriticAgent
from llm_clients import MockLLMClient
from golden_set.golden_data import GOLDEN_SET


# ---------- AGREEMENT LOGIC ----------

def compute_agreement(case: dict, critic_output) -> dict:
    """
    Compare the human's expected verdict with the Critic's verdict.

    Returns a dict with:
      - agrees (bool): does the verdict agree with expectation?
      - reason (str): why or why not
      - is_borderline (bool): true if the case was labeled BORDERLINE

    Borderline cases never count as disagreements — they're tie-breakers
    for measuring how the Critic handles ambiguity, not pass/fail tests.
    """
    expected = case["expected"]
    actual_verdict = critic_output.verdict.value
    actual_factual = critic_output.scores.factual_grounding

    # Borderline: PASS or REJECT both acceptable, only ACCEPT_WITH_WARNING
    # would be unusual on attempt 1 — but we still count it as "no disagreement"
    if expected["verdict"] == "BORDERLINE":
        return {
            "agrees": True,
            "is_borderline": True,
            "reason": f"Borderline case; Critic returned {actual_verdict} (acceptable)",
        }

    # Hallucination cases: must trigger hard fail AND have low factual_grounding
    if expected.get("hard_fail"):
        max_factual = expected.get("expected_factual_max", 4)
        hard_fail_ok = critic_output.hard_fail_triggered
        factual_ok = actual_factual <= max_factual
        verdict_ok = actual_verdict == "REJECT"
        agrees = hard_fail_ok and factual_ok and verdict_ok
        return {
            "agrees": agrees,
            "is_borderline": False,
            "reason": (
                f"Hallucination case: expected REJECT with hard_fail=True and "
                f"factual_grounding≤{max_factual}. "
                f"Got verdict={actual_verdict}, hard_fail={hard_fail_ok}, "
                f"factual_grounding={actual_factual}."
            ),
        }

    # Standard PASS or REJECT cases
    agrees = actual_verdict == expected["verdict"]
    return {
        "agrees": agrees,
        "is_borderline": False,
        "reason": (
            f"Expected {expected['verdict']}, got {actual_verdict}. "
            f"factual_grounding={actual_factual}, "
            f"weighted_avg={critic_output.weighted_average}."
        ),
    }


# ---------- RUNNER ----------

def run_case(agent: CriticAgent, case: dict, log_to_mlflow: bool = True) -> dict:
    """Run one case through the Critic and return enriched results."""
    inp = CriticInput(
        **case["input"],
        evaluation_config={"attempt_number": 1, "max_attempts": 3},
    )

    start = time.time()
    try:
        output = agent.evaluate(inp)
        elapsed_ms = int((time.time() - start) * 1000)
        agreement = compute_agreement(case, output)

        # Log to MLflow if available
        if log_to_mlflow:
            try:
                from evaluation.mlflow_logger import log_critic_run
                log_critic_run(
                    inp, output,
                    extra_tags={
                        "case_id": case["case_id"],
                        "expected_verdict": case["expected"]["verdict"],
                        "agrees": agreement["agrees"],
                    },
                )
            except Exception:
                pass  # Never let MLflow break the eval

        return {
            "case_id": case["case_id"],
            "language": case["language"],
            "topic": case["topic"],
            "expected_verdict": case["expected"]["verdict"],
            "actual_verdict": output.verdict.value,
            "actual_passed": output.passed,
            "hard_fail_triggered": output.hard_fail_triggered,
            "scores": output.scores.model_dump(),
            "weighted_average": output.weighted_average,
            "failed_dimensions": output.failed_dimensions,
            "feedback_summary": {
                dim: fb.issue for dim, fb in output.feedback.items()
            },
            "strengths": output.strengths,
            "agrees": agreement["agrees"],
            "is_borderline": agreement["is_borderline"],
            "agreement_reason": agreement["reason"],
            "expected_reasoning": case["expected"]["reasoning"],
            "elapsed_ms": elapsed_ms,
            "tokens_used": output.metadata.tokens_used,
            "error": None,
        }
    except Exception as e:
        return {
            "case_id": case["case_id"],
            "language": case["language"],
            "topic": case["topic"],
            "expected_verdict": case["expected"]["verdict"],
            "actual_verdict": None,
            "agrees": False,
            "is_borderline": False,
            "error": f"{type(e).__name__}: {e}",
            "elapsed_ms": int((time.time() - start) * 1000),
        }


def aggregate_metrics(results: list[dict]) -> dict:
    """Compute the headline quality metrics."""
    total = len(results)
    successful = [r for r in results if r.get("error") is None]
    errored = [r for r in results if r.get("error") is not None]

    non_borderline = [r for r in successful if not r.get("is_borderline")]
    agreements = sum(1 for r in non_borderline if r["agrees"])
    disagreements = [r for r in non_borderline if not r["agrees"]]

    agreement_rate = (agreements / len(non_borderline)) if non_borderline else 0.0

    # Per-category breakdown
    by_expected = {}
    for r in non_borderline:
        v = r["expected_verdict"]
        if v not in by_expected:
            by_expected[v] = {"total": 0, "agreed": 0}
        by_expected[v]["total"] += 1
        if r["agrees"]:
            by_expected[v]["agreed"] += 1

    avg_latency = (
        sum(r.get("elapsed_ms", 0) for r in successful) / len(successful)
        if successful else 0
    )
    total_tokens = sum(r.get("tokens_used", 0) for r in successful)

    return {
        "total_cases": total,
        "successful": len(successful),
        "errored": len(errored),
        "non_borderline_evaluated": len(non_borderline),
        "agreements": agreements,
        "disagreements": len(disagreements),
        "agreement_rate": round(agreement_rate, 3),
        "by_expected_verdict": by_expected,
        "avg_latency_ms": int(avg_latency),
        "total_tokens_used": total_tokens,
        "disagreement_case_ids": [r["case_id"] for r in disagreements],
        "errored_case_ids": [r["case_id"] for r in errored],
    }


# ---------- REPORT ----------

def render_markdown_report(metrics: dict, results: list[dict], mode: str) -> str:
    """Build a human-readable report of the run."""
    lines = []
    lines.append(f"# Critic Agent — Golden Set Evaluation Report\n")
    lines.append(f"**Mode:** {mode}")
    lines.append(f"**Run timestamp:** {datetime.now(timezone.utc).isoformat()}\n")

    lines.append("## Headline Metrics\n")
    lines.append(f"- **Agreement rate:** {metrics['agreement_rate']*100:.1f}% "
                 f"({metrics['agreements']}/{metrics['non_borderline_evaluated']} non-borderline cases)")
    lines.append(f"- **Disagreements:** {metrics['disagreements']}")
    lines.append(f"- **Errors:** {metrics['errored']}")
    lines.append(f"- **Avg latency:** {metrics['avg_latency_ms']}ms")
    lines.append(f"- **Total tokens:** {metrics['total_tokens_used']:,}\n")

    lines.append("## Agreement by Expected Verdict\n")
    lines.append("| Expected | Agreed | Total | Rate |")
    lines.append("|---|---|---|---|")
    for v, stats in metrics["by_expected_verdict"].items():
        rate = stats["agreed"] / stats["total"] if stats["total"] else 0
        lines.append(f"| {v} | {stats['agreed']} | {stats['total']} | {rate*100:.0f}% |")

    lines.append("\n## Per-Case Results\n")
    lines.append("| Case | Lang | Topic | Expected | Actual | Agrees | Notes |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in results:
        agree_icon = "✓" if r.get("agrees") else "✗"
        if r.get("is_borderline"):
            agree_icon = "≈"
        notes = r.get("error") or r.get("agreement_reason", "")
        notes = notes[:80] + ("..." if len(notes) > 80 else "")
        lines.append(
            f"| {r['case_id']} | {r['language']} | {r['topic']} | "
            f"{r['expected_verdict']} | {r.get('actual_verdict') or 'ERROR'} | "
            f"{agree_icon} | {notes} |"
        )

    if metrics["disagreement_case_ids"]:
        lines.append("\n## Disagreements — Detailed\n")
        for r in results:
            if not r.get("is_borderline") and not r.get("agrees") and r.get("error") is None:
                lines.append(f"### {r['case_id']}\n")
                lines.append(f"- **Expected:** {r['expected_verdict']}")
                lines.append(f"- **Actual:** {r['actual_verdict']}")
                lines.append(f"- **Scores:** {r['scores']}")
                lines.append(f"- **Human reasoning:** {r['expected_reasoning']}")
                if r.get("feedback_summary"):
                    lines.append(f"- **Critic feedback:** {r['feedback_summary']}")
                lines.append("")

    return "\n".join(lines)


# ---------- MAIN ----------

def make_mock_agent() -> CriticAgent:
    """
    Build a mock agent that returns a 'reasonably good' score for everything.
    Used for offline smoke-testing the runner — NOT for measuring real quality.
    """
    canned = json.dumps({
        "scores": {
            "naturalness_and_tone_match": 4,
            "factual_grounding": 5,
            "structural_coherence": 4,
            "engagement": 4,
        },
        "feedback": {},
        "strengths": ["Mock evaluation; not real judgment"],
    })
    return CriticAgent(llm_client=MockLLMClient(canned_response=canned))


def make_live_agent() -> CriticAgent:
    """Build a Groq-backed agent. Requires GROQ_API_KEY."""
    from llm_clients import GroqLLMClient
    return CriticAgent(llm_client=GroqLLMClient())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Use live Groq LLM")
    parser.add_argument("--mock", action="store_true", help="Use mock LLM (default)")
    args = parser.parse_args()

    use_live = args.live and not args.mock
    mode = "LIVE (Groq + Llama 3.3 70B)" if use_live else "MOCK"

    print(f"\n{'='*60}")
    print(f"Running golden set evaluation in {mode} mode")
    print(f"{'='*60}\n")

    agent = make_live_agent() if use_live else make_mock_agent()

    results = []
    for i, case in enumerate(GOLDEN_SET, 1):
        print(f"[{i:2d}/{len(GOLDEN_SET)}] {case['case_id']} ({case['language']}, "
              f"{case['topic']}) — expected {case['expected']['verdict']}...", end=" ", flush=True)
        result = run_case(agent, case)
        results.append(result)
        if result.get("error"):
            print(f"ERROR: {result['error']}")
        else:
            icon = "≈" if result["is_borderline"] else ("✓" if result["agrees"] else "✗")
            print(f"{result['actual_verdict']} {icon}")

    metrics = aggregate_metrics(results)

    print(f"\n{'='*60}")
    print(f"AGREEMENT RATE: {metrics['agreement_rate']*100:.1f}% "
          f"({metrics['agreements']}/{metrics['non_borderline_evaluated']})")
    print(f"Disagreements: {metrics['disagreement_case_ids']}")
    print(f"Errors: {metrics['errored_case_ids']}")
    print(f"Avg latency: {metrics['avg_latency_ms']}ms")
    print(f"{'='*60}\n")

    # Save artifacts
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    json_path = out_dir / f"run_{ts}_{'live' if use_live else 'mock'}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "results": results}, f, indent=2, ensure_ascii=False)

    md_path = out_dir / f"run_{ts}_{'live' if use_live else 'mock'}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_markdown_report(metrics, results, mode))

    print(f"Saved: {json_path}")
    print(f"Saved: {md_path}")

    # Log aggregate run to MLflow
    try:
        from evaluation.mlflow_logger import log_golden_set_run
        run_id = log_golden_set_run(metrics, results, mode)
        if run_id:
            print(f"MLflow run logged: {run_id}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
