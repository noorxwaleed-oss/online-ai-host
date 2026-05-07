from prompts import textGeneration_prompt
from llms import generateTextLlm

textGeneration_chat_chain= textGeneration_prompt | generateTextLlm 