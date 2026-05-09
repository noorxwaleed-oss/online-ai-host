import asyncio

from typing import TypedDict
from typing import List
from typing import Optional
from typing import Dict
from typing import Any

from langgraph.graph import StateGraph
from langgraph.graph import END

from shared.http_client import post
from shared.config import *


# =========================================
# STATE
# =========================================

class AgentState(TypedDict):

    source_url: str
    voice_id: str

    key_points: List[str]
    source_meta: Dict[str, Any]

    voice_metadata: Dict[str, Any]

    script_turns: List[Dict[str, str]]

    script_id: str
    version: int

    attempt_number: int
    max_attempts: int

    previous_feedback: Optional[Dict[str, Any]]

    verdict: str
    passed: bool
    hard_fail_triggered: bool

    final_assets: Dict[str, str]

    error_message: Optional[str]


# =========================================
# STEP 1
# TEXT EXTRACTION
# =========================================

async def text_extraction_node(state: AgentState):

    print("STEP 1 -> TEXT EXTRACTION")

    extracted = await post(
        TEXT_AGENT_URL,
        {
            "url": state["source_url"]
        }
    )

    return {
        "key_points": extracted["key_points"],
        "source_meta": extracted["source_meta"],
        "script_id": "scr_001",
        "version": 0
    }


# =========================================
# STEP 2
# LOAD VOICE
# =========================================

async def load_voice_node(state: AgentState):

    print("STEP 2 -> LOAD VOICE")

    voice_metadata = {
        "voice_id": state["voice_id"],
        "name": "Salma",
        "accent": "American",
        "tone_label": "casual energetic",
        "language": "en"
    }

    return {
        "voice_metadata": voice_metadata
    }


# =========================================
# STEP 3
# SCRIPTWRITER
# =========================================

async def scriptwriter_node(state: AgentState):

    print(f"STEP 3 -> SCRIPTWRITER ATTEMPT {state['attempt_number'] + 1}")

    response = await post(
        SCRIPT_AGENT_URL,
        {
            "key_points": state["key_points"],
            "voice_metadata": state["voice_metadata"],
            "previous_feedback": state["previous_feedback"]
        }
    )

    return {
        "script_turns": response["turns"],
        "attempt_number": state["attempt_number"] + 1,
        "version": state["version"] + 1
    }


# =========================================
# STEP 4
# CRITIC
# =========================================

async def critic_node(state: AgentState):

    print("STEP 4 -> CRITIC")

    critique = await post(
        CRITIC_AGENT_URL,
        {
            "script": {
                "script_id": state["script_id"],
                "version": state["version"],
                "turns": state["script_turns"]
            },

            "key_points": state["key_points"],

            "source_meta": state["source_meta"],

            "voice_metadata": state["voice_metadata"],

            "evaluation_config": {
                "attempt_number": state["attempt_number"],
                "max_attempts": state["max_attempts"],
                "previous_feedback": state["previous_feedback"]
            }
        }
    )

    return {
        "verdict": critique["verdict"],
        "passed": critique["passed"],
        "hard_fail_triggered": critique["hard_fail_triggered"],
        "previous_feedback": critique["feedback"]
    }


# =========================================
# STEP 5
# PRODUCTION
# =========================================

async def production_node(state: AgentState):

    print("STEP 5 -> PRODUCTION")

    audio_task = post(
        AUDIO_AGENT_URL,
        {
            "turns": state["script_turns"],
            "voice_id": state["voice_id"]
        }
    )

    cover_task = post(
        COVER_AGENT_URL,
        {
            "turns": state["script_turns"]
        }
    )

    audio_result, cover_result = await asyncio.gather(
        audio_task,
        cover_task
    )

    return {
        "final_assets": {
            "audio": audio_result["audio_url"],
            "cover": cover_result["cover_url"]
        }
    }


# =========================================
# FAILURE
# =========================================

async def failure_node(state: AgentState):

    print("FAILED AFTER MAX ATTEMPTS")

    return {
        "error_message": "Script generation failed after 3 attempts."
    }


# =========================================
# ROUTER
# =========================================

def router(state: AgentState):

    if state["verdict"] in [
        "PASS",
        "ACCEPT_WITH_WARNING"
    ]:
        return "approved"

    if state["attempt_number"] < state["max_attempts"]:
        return "retry"

    return "failed"


# =========================================
# BUILD GRAPH
# =========================================

workflow = StateGraph(AgentState)

workflow.add_node(
    "text_extractor",
    text_extraction_node
)

workflow.add_node(
    "voice_loader",
    load_voice_node
)

workflow.add_node(
    "scriptwriter",
    scriptwriter_node
)

workflow.add_node(
    "critic",
    critic_node
)

workflow.add_node(
    "producer",
    production_node
)

workflow.add_node(
    "failure",
    failure_node
)

workflow.set_entry_point(
    "text_extractor"
)

workflow.add_edge(
    "text_extractor",
    "voice_loader"
)

workflow.add_edge(
    "voice_loader",
    "scriptwriter"
)

workflow.add_edge(
    "scriptwriter",
    "critic"
)

workflow.add_conditional_edges(
    "critic",
    router,
    {
        "approved": "producer",
        "retry": "scriptwriter",
        "failed": "failure"
    }
)

workflow.add_edge(
    "producer",
    END
)

workflow.add_edge(
    "failure",
    END
)

app_graph = workflow.compile()