import json
from openai import OpenAI
from config import OPENROUTER_API_KEY, BASE_URL, MODEL_NAME, ANALYZER_PROMPT, TRANSLATOR_PROMPT

client = OpenAI(base_url=BASE_URL, api_key=OPENROUTER_API_KEY)

def run_smart_analysis(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 15})
    relevant_chunks = retriever.invoke("podcast main topics discussions arguments insights stories")
    context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])

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