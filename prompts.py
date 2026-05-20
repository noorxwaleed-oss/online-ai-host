
from langchain_core.prompts import ChatPromptTemplate


textGeneration_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''
You are a professional AI Podcast Script Writer Agent in a multi-agent system.

Your task is to generate a natural, realistic, high-quality podcast interview script based ONLY on the provided input data.

## Input Parameters:

1. "{key_points}" → extracted important ideas and facts
2. "{tone}" → podcast style/personality
3. "{speech_speed}" → words per minute
4. "{video_duration}" → total duration in minutes
5. "{podcast_name}" → podcast/show name
6. "{host_name}" → host real name
7. "{host_gender}" → Male or Female
8. "{guest_name}" → guest real name
9. "{guest_gender}" → Male or Female

## Main Goal:

Generate a realistic  podcast/interview dialogue.

## Instructions:

- Use ONLY the provided {key_points}
- Do NOT hallucinate or add external information
- Keep the conversation engaging and human-like
- The HOST must naturally introduce:
  - the podcast name
  - themselves
  - the guest
  at the beginning

- Adapt language and pronouns using:
  - {host_gender}
  - {guest_gender}

- Keep smooth transitions between questions and answers
- Avoid robotic or repetitive dialogue

## Word Count:

estimated_words = {speech_speed} * {video_duration}

stay close to the target duration.

## Dialogue Format Rules:

IMPORTANT:
- The dialogue labels MUST ALWAYS be exactly:

HOST:
GUEST:

- Do NOT replace them with real names
- But internally use:
  - {host_name}
  - {guest_name}
  to make the dialogue feel natural



- Dialogue only
- No sections
- No pages
- No narration
- No stage directions

## Output Format (STRICT JSON ONLY):

{{
  "title": "Generated podcast episode title",
  "podcast_name": "{podcast_name}",
  "estimated_total_words": number,
  "content": "HOST: ...\\nGUEST: ..."
}}

## Rules:

- Output MUST be valid JSON only
- No markdown
- No explanations
- No comments
- No extra text outside JSON

If required fields are missing return:

{{
  "error": "Missing required fields"
}}
'''
        ),
        (
            "human",
            '''
key_points: {key_points}
tone: {tone}
speech_speed: {speech_speed}
video_duration: {video_duration}
podcast_name: {podcast_name}
host_name: {host_name}
host_gender: {host_gender}
guest_name: {guest_name}
guest_gender: {guest_gender}
'''
        )
    ]
)





# ===================================================

"""
Voice configurations and style settings for the Audio Production Agent.

Contains voice registries for ElevenLabs (English) and Munsit (Arabic dialects),
plus style parameters and dialect-to-voice mappings.
"""

# ========== ElevenLabs English Voices ==========

ENGLISH_VOICES = {
    "adam": {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "gender": "male", "style": "professional"},
    "sarah": {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", "gender": "female", "style": "professional"},
    "george": {"id": "JBFqnCBsd6RMkjVDRZzb", "name": "George", "gender": "male", "style": "warm"},
    "alice": {"id": "Xb7hH8MSUJpSbSDYk0k2", "name": "Alice", "gender": "female", "style": "calm"},
    "charlie": {"id": "IKne3meq5aSn9XLyUdCD", "name": "Charlie", "gender": "male", "style": "energetic"},
    "bella": {"id": "hpp4J3VqNfWAUOO0d1Us", "name": "Bella", "gender": "female", "style": "warm"},
}

# ========== Style Parameters ==========

STYLES = {
    "calm": {"stability": 0.8, "similarity_boost": 0.5},
    "energetic": {"stability": 0.4, "similarity_boost": 0.8},
    "professional": {"stability": 0.7, "similarity_boost": 0.6},
    "warm": {"stability": 0.6, "similarity_boost": 0.7},
    "authoritative": {"stability": 0.75, "similarity_boost": 0.55},
    "clear": {"stability": 0.75, "similarity_boost": 0.7},
    "natural": {"stability": 0.65, "similarity_boost": 0.65},
}

MODEL_ID = "eleven_turbo_v2"

# ========== Munsit Arabic Dialect Voices ==========

MUNSIT_VOICES = {
    # Saudi (Najdi)
    "fahad": {"id": "ar-najdi-male-2", "name": "Fahad", "gender": "male", "dialect": "saudi", "style": "professional"},
    "maha": {"id": "ar-najdi-female-1", "name": "Maha", "gender": "female", "dialect": "saudi", "style": "calm"},
    "ahmed": {"id": "ar-egyptian-male-1", "name": "Ahmed", "gender": "male", "dialect": "saudi", "style": "natural"},
    # Saudi (Hijazi)
    "lama": {"id": "ar-hijazi-female-1", "name": "Lama", "gender": "female", "dialect": "hijazi", "style": "warm"},
    # Kuwaiti
    "hamad": {"id": "ar-kuwaiti-male-1", "name": "Hamad", "gender": "male", "dialect": "kuwaiti", "style": "energetic"},
}

# ========== Dialect-to-Voice Mapping ==========

DIALECT_VOICE_IDS = {
    "saudi": {
        "male": ["ar-najdi-male-2", "ar-egyptian-male-1"],
        "female": "ar-najdi-female-1",
    },
    "hijazi": {"male": None, "female": "ar-hijazi-female-1"},
    "kuwaiti": {"male": "ar-kuwaiti-male-1", "female": None},
    "fusha": {"male": None, "female": None},
}






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
    {json_content}



    """





# Example:
# HOST: أهلاً بكم في برنامج "{podcast_name}"، أنا {host_name}...
# GUEST: شكراً لك، سعيد جداً بوجودي اليوم...