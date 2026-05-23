import json
import re
from urllib.parse import urlparse
import os

def tojson(text):
    if hasattr(text, 'content'):
        return json.loads(text.content)
    return json.loads(text)

def parse_script_for_save(text: str):
    lines = text.split("\n")
    return {
        "content": text,
        "lines": lines
    }

def to_str_script(script):
    if isinstance(script, dict) and "content" in script:
        return script["content"]
    return str(script)

def detect_input_type(value: str):
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        return "url"
    elif os.path.isfile(value) and value.lower().endswith(".pdf"):
        return "pdf"
    return "unknown"

def parse_script_turns(raw_text: str) -> list:
    """Parse raw text into Host/Guest turns."""
    lines = raw_text.strip().split('\n')
    script = []
    current_speaker = None
    current_text = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        host_match = re.match(r'^(?:Host|HOST|host)\s*:\s*(.*)$', line)
        guest_match = re.match(r'^(?:Guest|GUEST|guest)\s*:\s*(.*)$', line)

        if host_match:
            if current_speaker and current_text:
                script.append({'speaker': current_speaker, 'text': current_text.strip()})
            current_speaker = 'host'
            current_text = host_match.group(1)
        elif guest_match:
            if current_speaker and current_text:
                script.append({'speaker': current_speaker, 'text': current_text.strip()})
            current_speaker = 'guest'
            current_text = guest_match.group(1)
        else:
            if current_speaker:
                current_text += " " + line

    if current_speaker and current_text:
        script.append({'speaker': current_speaker, 'text': current_text.strip()})

    return script

def extract_json(text):
    match = re.search(r'(\{.*\})', str(text), re.DOTALL)
    return json.loads(match.group(1)) if match else {}
