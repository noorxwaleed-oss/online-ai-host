from langchain_openai import ChatOpenAI
from backend.config.settings import settings

generateTextLlm = ChatOpenAI(
    model=settings.TEXTGENERATION_MODEL,
    api_key=settings.TEXTGENERATION_HF_TOKEN,
    base_url=settings.TEXTGENERATION_BASE_URL,
    temperature=0.2
)

# Constants for analysis core
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
