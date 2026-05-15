from prompts import textGeneration_prompt
from llms import generateTextLlm
from prompts import clipsGeneration_prompt
textGeneration_chat_chain= textGeneration_prompt | generateTextLlm 
clipsGeneration_chat_chain = clipsGeneration_prompt | generateTextLlm
"""Chain wiring for the Audio Production Agent."""
from audio import text_to_speech
from llms import get_elevenlabs_key, get_munsit_key
from prompts import ENGLISH_VOICES, MUNSIT_VOICES, STYLES
from utils import upload_to_cloudinary

# from prompts import SYSTEM_PROMPT, build_user_prompt
# from llms import GroqLLMClient
# from critic_agent import CriticAgent

# critic_llm = GroqLLMClient()
# critic_agent = CriticAgent(llm_client=critic_llm)