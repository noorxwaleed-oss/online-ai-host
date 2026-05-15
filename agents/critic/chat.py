from prompts import SYSTEM_PROMPT, build_user_prompt
from llms import GroqLLMClient
from critic_agent import CriticAgent

critic_llm = GroqLLMClient()
critic_agent = CriticAgent(llm_client=critic_llm)
