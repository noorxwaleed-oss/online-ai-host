from backend.agents.llms import generateTextLlm
from backend.agents.prompts import textGeneration_prompt

textGeneration_chat_chain = textGeneration_prompt | generateTextLlm
