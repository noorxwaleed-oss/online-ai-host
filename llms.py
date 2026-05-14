from langchain_openai import ChatOpenAI
from config import textGeneration_model, textGeneration_HF_token , textGeneration_base_url

generateTextLlm = ChatOpenAI(model=textGeneration_model
                 , api_key=textGeneration_HF_token
                 ,base_url=textGeneration_base_url
                 ,temperature=0.2)
