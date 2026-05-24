import os
import hashlib
import json
import re
import warnings

from llms import MODEL_NAME
from utils import load_data
from analyzer import run_smart_analysis, translator



source_input  = "" 
# user_language_choice = "Arabic"

def extract_json(text):

    match = re.search(r'(\{.*\})', str(text), re.DOTALL)
    return json.loads(match.group(1)) if match else {}


def _detect_output_language(analysis: dict) -> str:
    """Inspect the analyzer's output text to detect whether it's actually
    Arabic or English, rather than trusting the LLM's self-reported
    'source_language' field (which is often wrong when the model silently
    translates the content to English)."""
    sample_parts = []
    for topic in (analysis.get("topics") or [])[:5]:
        sample_parts.append(str(topic.get("title", "")))
        sample_parts.append(str(topic.get("insight", "")))
        for kp in (topic.get("key_points") or [])[:3]:
            sample_parts.append(str(kp))
    sample = " ".join(sample_parts)
    if not sample.strip():
        return "unknown"
    arabic_chars = sum(1 for c in sample if "؀" <= c <= "ۿ")
    latin_chars = sum(1 for c in sample if ("a" <= c.lower() <= "z"))
    if arabic_chars + latin_chars == 0:
        return "unknown"
    return "arabic" if arabic_chars > latin_chars else "english"


def agent_analyzer(source_input, user_language_choice ):


    try:
        # 1. Load Data
        raw_data = load_data(source_input)

        # 2. Run Analysi
        analysis_raw = run_smart_analysis(raw_data)
        analysis = extract_json(analysis_raw)

        # 3. Translate if the ACTUAL output language doesn't match what the
        #    user asked for. We do NOT rely on the LLM's self-reported
        #    `source_language` because it is often inconsistent — the LLM
        #    reports "Arabic" but silently outputs the topics in English.
        target_lang = user_language_choice.lower()
        detected = _detect_output_language(analysis)
        print(f"   Analyzer self-reported: {analysis.get('source_language')!r} | "
              f"Detected from content: {detected!r} | Target: {target_lang!r}")
        if detected != "unknown" and detected != target_lang:
            print(f"   Translating analyzer output -> {target_lang}")
            translation_raw = translator(analysis, target_lang=user_language_choice)
            analysis = extract_json(translation_raw)

        # 4. Final Output
        print(f"✅ Success! Extracted {len(analysis.get('topics', []))} topics.\n" + "-"*40)
        resulte = json.dumps(analysis, indent=2, ensure_ascii=False)
        print(resulte)
        return resulte
        # print(json.dumps(analysis, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Error: {e}")


# if __name__ == "__main__":
#     main()