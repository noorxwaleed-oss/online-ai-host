from fastapi import FastAPI
from orchestrator.graph import app_graph

app = FastAPI(
    title="AI Podcast Orchestrator"
)

@app.post("/run")
async def run_pipeline(data: dict):

    result = await app_graph.ainvoke({
        "source_url": data["source_url"],
        "voice_id": data["voice_id"],
        "attempt_number": 0,
        "max_attempts": 3,
        "previous_feedback": None
    })

    return result