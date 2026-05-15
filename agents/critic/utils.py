"""Utility helpers for the Critic Agent."""

import json


def tojson(text):
    """Parse LLM message content as JSON."""
    data = json.loads(text.content)
    return data


def print_result(result):
    """Pretty-print a CriticOutput as JSON."""
    print(json.dumps(result.model_dump(), indent=4, ensure_ascii=False, default=str))
