from dotenv import load_dotenv
import os
load_dotenv()
textGeneration_model = os.getenv("TEXTGENERATION_MODEL")
textGeneration_HF_token = os.getenv("TEXTGENERATION_HF_token")
textGeneration_base_url = os.getenv("TEXTGENERATION_BASE_URL")