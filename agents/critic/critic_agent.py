"""
Critic Agent — the main class.

Public interface:
    critic = CriticAgent(llm_client=...)
    result: CriticOutput = critic.evaluate(critic_input)

Design principles:
- Stateless: each evaluate() call is independent
- Fail loud: bad inputs raise, bad LLM outputs raise (caught and retried)
- Pluggable LLM client: pass any object with a .complete(system, user) method
- Logs everything needed for MLflow tracking
"""

import json
import time
from datetime import datetime, timezone
from typing import Protocol

from schemas.models import (
    CriticInput,
    CriticOutput,
    CriticMetadata,
    DimensionScores,
    DimensionFeedback,
    Verdict,
)
from rubric import (
    compute_weighted_average,
    decide_verdict,
    find_failed_dimensions,
)
from prompts.critic_prompt import SYSTEM_PROMPT, build_user_prompt


# ---------- LLM CLIENT PROTOCOL ----------
# We define an interface, not a concrete class.
# This means you can swap Groq → OpenAI → local Llama without changing the agent.

class LLMClient(Protocol):
    """Any LLM client must implement this method."""
    model_name: str

    def complete(self, system_prompt: str, user_prompt: str) -> tuple[str, int]:
        """
        Returns: (response_text, tokens_used)
        Must raise on failure.
        """
        ...


# ---------- CRITIC AGENT ----------

class CriticAgent:
    """Quality Control critic for podcast scripts."""

    def __init__(self, llm_client: LLMClient, max_parse_retries: int = 2):
        self.llm = llm_client
        self.max_parse_retries = max_parse_retries

    def evaluate(self, inp: CriticInput) -> CriticOutput:
        """Run a full evaluation. Returns a CriticOutput."""
        start_time = time.time()

        system_prompt = SYSTEM_PROMPT
        user_prompt = build_user_prompt(inp)

        # LLM call with parse retry (handles the rare case of malformed JSON)
        raw_response, tokens_used = self._call_llm_with_retry(
            system_prompt, user_prompt
        )

        # Parse the LLM's JSON response into validated objects
        scores, feedback_dict, strengths = self._parse_response(raw_response)

        # Apply our deterministic pass/fail logic (NOT the LLM's job)
        verdict, passed, hard_fail = decide_verdict(
            scores=scores,
            attempt_number=inp.evaluation_config.attempt_number,
            max_attempts=inp.evaluation_config.max_attempts,
        )

        weighted_avg = compute_weighted_average(scores)
        failed_dims = find_failed_dimensions(scores)

        elapsed_ms = int((time.time() - start_time) * 1000)

        return CriticOutput(
            script_id=inp.script.script_id,
            version=inp.script.version,
            verdict=verdict,
            passed=passed,
            scores=scores,
            weighted_average=weighted_avg,
            hard_fail_triggered=hard_fail,
            failed_dimensions=failed_dims,
            feedback=feedback_dict,
            strengths=strengths,
            metadata=CriticMetadata(
                evaluator_model=self.llm.model_name,
                evaluation_time_ms=elapsed_ms,
                tokens_used=tokens_used,
                timestamp=datetime.now(timezone.utc),
            ),
        )

    # ---------- internal helpers ----------

    def _call_llm_with_retry(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[str, int]:
        """Calls the LLM. Retries up to max_parse_retries on JSON parse failure."""
        last_error: Exception | None = None
        for attempt in range(self.max_parse_retries + 1):
            try:
                response, tokens = self.llm.complete(system_prompt, user_prompt)
                # Quick sanity check: must contain a JSON object
                if "{" in response and "}" in response:
                    return response, tokens
                last_error = ValueError("Response contained no JSON object")
            except Exception as e:
                last_error = e
        raise RuntimeError(
            f"LLM failed to return valid response after {self.max_parse_retries + 1} attempts: {last_error}"
        )

    def _parse_response(
        self, raw: str
    ) -> tuple[DimensionScores, dict[str, DimensionFeedback], list[str]]:
        """
        Extract and validate the LLM's JSON.
        We strip any accidental markdown fences before parsing.
        """
        # Strip common LLM mistakes: ```json fences, leading/trailing prose
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            # Remove first line (```json or ```) and last line (```)
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned
        # Find the outermost JSON object
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"No JSON object found in LLM response: {raw[:200]}")
        cleaned = cleaned[start : end + 1]

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from LLM: {e}\nRaw: {raw[:300]}")

        # Validate structure
        if "scores" not in parsed:
            raise ValueError("LLM response missing 'scores' field")

        scores = DimensionScores(**parsed["scores"])

        feedback_dict: dict[str, DimensionFeedback] = {}
        for dim, fb in parsed.get("feedback", {}).items():
            feedback_dict[dim] = DimensionFeedback(**fb)

        strengths = parsed.get("strengths", [])
        if not isinstance(strengths, list):
            strengths = []

        return scores, feedback_dict, strengths
