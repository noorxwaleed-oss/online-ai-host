import json
from backend.utils.helpers import extract_json
from backend.utils.loaders import load_data
from backend.agents.analysis_core import run_smart_analysis, translator

def agent_analyzer(source_input, user_language_choice):
    try:
        # 1. Load Data
        raw_data = load_data(source_input)
        
        # 2. Run Analysis
        analysis_raw = run_smart_analysis(raw_data)
        analysis = extract_json(analysis_raw)

        # 3. Translate if needed
        source_lang = analysis.get("source_language", "unknown").lower()
        if source_lang != user_language_choice.lower():
            translation_raw = translator(analysis, target_lang=user_language_choice)
            analysis = extract_json(translation_raw)

        return json.dumps(analysis, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"❌ Error in agent_analyzer: {e}")
        raise
