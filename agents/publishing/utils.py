"""Utility helpers for the Publishing Agent."""

import json


def tojson(text):
    """Parse message content as JSON."""
    data = json.loads(text.content)
    return data


def print_result(result):
    """Pretty-print a PublishingOutput as JSON."""
    print(json.dumps(result.model_dump(), indent=4, ensure_ascii=False, default=str))
