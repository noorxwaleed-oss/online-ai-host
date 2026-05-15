import json
from openai import OpenAI
from prompts import ANALYZER_PROMPT, TRANSLATOR_PROMPT
from llms import BASE_URL, MODEL_NAME
from config import OPENROUTER_API_KEY

client = OpenAI(base_url=BASE_URL, api_key=OPENROUTER_API_KEY)

def run_smart_analysis(content):
    if isinstance(content, list):
        context = "\n\n".join([doc.page_content for doc in content])
    else:
        context = content
    
    
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": ANALYZER_PROMPT.format(context=context)}],
        temperature=0.3
    )
    return completion.choices[0].message.content

def translator(analysis_json, target_lang):
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": TRANSLATOR_PROMPT.format(target_lang=target_lang, json_content=json.dumps(analysis_json, ensure_ascii=False))}],
        temperature=0.1
    )
    return completion.choices[0].message.content