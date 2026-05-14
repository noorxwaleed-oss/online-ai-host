import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


ANALYZER_PROMPT =  """
    You are a Content Analyzer Agent. Your goal is to prepare material for a professional podcast.

    YOUR TASK:
    - Detect and preserve the ORIGINAL language of the context.
    - Analyze the FULL context deeply.
    - Extract 20 to 30 unique, high-value topics from the context.

    INSTRUCTION FOR SHORT CONTENT:
    - Assess the depth of the provided 'Context'.
    - Focus only on information explicitly or strongly implied in context.
    - If context is rich:
      extract 20-30 topics
      set "content_status" to "sufficient"

    - If context is limited:
      extract only 10 strong topics
      set "content_status" to "limited"

    Rules:
    - NEVER translate the content.
    - ALL output MUST remain in the SAME language as the context.
    - Avoid hallucination.
    - Do not invent information.
    - The entire output content MUST be in language of the provided 'contex'.
    - STRICT PROHIBITION: Do NOT use any Chinese characters (中文), even if the model defaults to it.
    - Focus on facts, stories, and controversial points suitable for a professional dialogue.
    - Return ONLY valid JSON.




    Context: {context}

    Format:
    {{
      "source_language": "",
      "content_status": "",
      "topics": [
        {{
          "title": "Topic Title",
          "key_points": ["Point 1", "Point 2"],
          "insight": "Deep takeaway",
          "discussion_angles": ["Question for the host", "Counter-argument"]
        }}
      ]
    }}
    """


TRANSLATOR_PROMPT = """
    You are a professional JSON translator.

    TASK:
    Translate the JSON content into {target_lang}.

    - Preserve ONLY:
    1. Proper nouns (names of people, places, organizations)
    2. Brand names
    3. Fixed international terms that do not have a common translation in {target_lang}

    STRICT RULES:
    - The goal is natural, human-like bilingual fluency, not literal translation.
    - Preserve JSON structure EXACTLY.
    - Do NOT summarize.
    - Do NOT add explanations.
    - Do NOT remove fields.
    - Translate ONLY text values.
    - Keep tone natural and professional.
    - Return ONLY valid JSON.

    JSON:
    {json.dumps(analysis_json, ensure_ascii=False)}
    """

