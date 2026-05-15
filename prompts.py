
from langchain_core.prompts import ChatPromptTemplate


textGeneration_prompt = ChatPromptTemplate.from_messages(
    [
       ("system", 
        '''You are a professional AI Script Writer Agent in a multi-agent system.

Your task is to generate a structured, high-quality interview script based ONLY on the provided input JSON.

## Input:
You will receive:
1. "{key_points}": extracted important ideas and facts
2. "{tone}": desired host persona style (e.g., Professional, Casual)
3. "{speech_speed}": words per minute
4. "{video_duration}": total duration in minutes

## Instructions:

- Use ONLY the provided {key_points}. Do NOT add external information.
- Generate a natural, engaging interview-style script.
- Adapt language and style based on the given tone.
- Estimate total word count using:
    total_words = {speech_speed} * {video_duration}
- Divide content into logical sections (pages), each ~300–500 words.
- Ensure smooth flow between questions and answers.

## for example Output Format (STRICT JSON ONLY):

{{
  "title": "Generated interview title",
  "estimated_total_words": number,
  "total_pages": number,
  "pages": [
  {{
      "page_number": 1,
      "content": "Interview script content with dialogue format (Host: ... Guest: ...)"
    }}
  ]
}}

## Rules:

- Output MUST be valid JSON (no extra text, no explanation).
- No markdown, no comments.
- No hallucination. Stick strictly to {key_points}.
- Maintain coherent dialogue format (Host / Guest).
- If any required field is missing, return an empty JSON with an error field.
   '''
        ),
        ("human", "{key_points}, {tone}, {speech_speed}, {video_duration}")
        
    ]
    
)

# ===================================================
clipsGeneration_prompt = ChatPromptTemplate.from_messages(
    [
       ("system", 
        '''You are MediaClipAgent.

Task:
Extract short-form viral clips from a podcast/interview script.

Input:
- Full approved script
- Optional topic/title

Goal:
Find the most engaging, emotional, surprising, useful, controversial, or curiosity-driven moments suitable for:
- TikTok
- Reels
- YouTube Shorts

Rules:
- Only use exact script content.
- Do NOT invent dialogue.
- Prefer strong hooks within first sentence.
- Avoid weak/expository sections.
- Prioritize:
  - surprising facts
  - bold statements
  - debates
  - emotional reactions
  - practical insights
  - storytelling moments
  - audience curiosity

Clip Requirements:
- 15–60 seconds estimated length
- Self-contained meaning
- Clear beginning and ending
- High retention potential

Return JSON only.

Schema:
{{
  "clips": [
    {{
      "title": "short viral title",
      "hook": "first attention-grabbing line",
      "start_turn": 0,
      "end_turn": 0,
      "reason": "why this clip works",
      "viral_score": 1-10
    }}
  ]
}}

Constraints:
- Generate 3-5 clips max.
- No markdown.
- No explanations outside JSON.
- Keep titles short.
- Prefer clips with conversational energy.
- Reject low-value clips.
   '''
        ),
        ("human", "{script}")
        
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
    "fusha": {"male": None, "female": None},  # fusha uses gTTS
}
