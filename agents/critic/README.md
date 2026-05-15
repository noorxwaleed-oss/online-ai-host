# Critic Agent (Quality Control) — v1.2

Quality Control agent for the AI Host Interview project.
Evaluates AI-generated podcast scripts across 4 dimensions, returns
structured feedback, and supports the Generator↔Critic refinement loop.

**Owner:** Maryam · **Status:** v1.2 (matches workflow PDF v1.2)

---

## Project structure

```
critic_agent_v12/
├── .example.env               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── chat.py                    # Chain wiring (imports prompts + LLM)
├── config.py                  # Centralized configuration
├── critic_agent.py            # Main CriticAgent class
├── golden_data.py             # 10 hand-labeled scripts for validation
├── llms.py                    # GroqLLMClient + MockLLMClient
├── mlflow_logger.py           # MLflow integration (Milestone 4)
├── models.py                  # Pydantic I/O contract (v1.2)
├── prompts.py                 # LLM prompt construction
├── quickstart.py              # Live demo (needs GROQ_API_KEY)
├── rubric.py                  # Scoring rubric + pass/fail logic
├── run_golden_set.py          # Golden set evaluation runner
├── test_critic.py             # 13 unit tests (no API key needed)
└── utils.py                   # Utility helpers
```

---

## Setup (one time)

```bash
pip install pydantic groq mlflow pytest
export GROQ_API_KEY=your_groq_key_here   # Get free key at console.groq.com
```

For Arabic test cases, no extra setup needed — Llama 3.3 70B handles Arabic natively.

---

## Usage

### Run unit tests (no API key needed)

```bash
cd critic_agent_v12
python test_critic.py
```

Should print 13 passed, 0 failed.

### Run the live demo (requires GROQ_API_KEY)

```bash
python quickstart.py
```

Sends one sample script to the live Critic and prints the evaluation.

### Run golden set evaluation in MOCK mode (offline, no API key)

```bash
python run_golden_set.py --mock
```

This will give you a baseline. The mock returns the same canned scores for
everything — your live LLM must significantly beat this baseline to prove
it's actually evaluating intelligently.

### Run golden set evaluation in LIVE mode (uses Groq API)

```bash
python run_golden_set.py --live
```

This runs all 10 cases through Llama 3.3 70B and produces:
- `evaluation/results/run_<timestamp>_live.json` — full per-case data
- `evaluation/results/run_<timestamp>_live.md` — human-readable report
- An MLflow run (if MLflow is installed and configured)

Expected runtime: ~30-60 seconds (Groq is fast).

### View MLflow dashboard (optional, for Milestone 4)

```bash
mlflow ui
```

Then open `http://127.0.0.1:5000` in your browser. You'll see all your
evaluation runs side by side — perfect for the final report.

---

## Quality dimensions (v1.2)

| Dimension | Weight | Hard-gated? |
|---|---|---|
| Naturalness & Tone Match | 0.30 | No |
| Factual Grounding | 0.25 | **Yes (must = 5)** |
| Structural Coherence | 0.20 | No |
| Engagement | 0.25 | No |

A script PASSES when:
- `factual_grounding == 5` (zero tolerance for hallucination)
- AND `weighted_average >= 3.5`
- AND no other dimension scored below 2

If the script fails on attempt 3 (max), it returns `ACCEPT_WITH_WARNING`
**unless** it has a hard fail (hallucination) — those always reject.

---

## Golden set composition

10 hand-labeled scripts:
- 4 GOOD (should PASS)
- 3 BAD non-hallucination (should REJECT for stylistic / structural reasons)
- 2 HALLUCINATION (should hard-fail on factual grounding)
- 1 BORDERLINE (genuinely ambiguous; either verdict acceptable)

Languages: 8 English, 2 Arabic.
Topics: tech, health, business, education, climate, history.

The mock baseline is **44.4% agreement**. A real LLM should achieve **70%+**
to demonstrate quality. **80%+** is excellent.

---

## Integration with the team

The Critic accepts `CriticInput` and returns `CriticOutput`. See
`schemas/models.py` for exact shapes.

- **Asmaa (Orchestrator)** routes scripts to the Critic and handles the
  refinement loop. She's the only agent that talks to the Critic.
- **Aliaa (Scriptwriter)** must produce scripts in the `Script` model format
  (turns[] with speaker + text).
- **Aya (Audio Production)** owns the `VoiceMetadata` schema; the Orchestrator
  reads the user's voice choice from her DB and forwards it.
- **Nour (Text Extraction)** produces the `key_points` list — the whitelist
  for hallucination checking.
