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
def agent_analyzer(source_input, user_language_choice ):

    
    try:
        # 1. Load Data
        raw_data = load_data(source_input)
        
        # 2. Run Analysi
        analysis_raw = run_smart_analysis(raw_data)
        analysis = extract_json(analysis_raw)

        # 3. Translate if needed
        source_lang = analysis.get("source_language", "unknown").lower()
        if source_lang != user_language_choice.lower():
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