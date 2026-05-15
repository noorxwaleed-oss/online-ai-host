from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import os
load_dotenv()
textGeneration_model = os.getenv("TEXTGENERATION_MODEL")
textGeneration_HF_token = os.getenv("TEXTGENERATION_HF_token")
textGeneration_base_url = os.getenv("TEXTGENERATION_BASE_URL")
elevenlabs_api_key1 = os.getenv("ELEVENLABS_API_KEY1")
elevenlabs_api_key2 = os.getenv("ELEVENLABS_API_KEY2")
elevenlabs_api_key3 = os.getenv("ELEVENLABS_API_KEY3")
munsit_api_key1 = os.getenv("MUNSIT_API_KEY1")
munsit_api_key2 = os.getenv("MUNSIT_API_KEY2")
munsit_api_key3 = os.getenv("MUNSIT_API_KEY3")


cloudinary_config =cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


ELEVENLABS_KEYS = []
for i in range(1, 10):
    key = os.getenv(f"ELEVENLABS_API_KEY{i}")
    if key:
        ELEVENLABS_KEYS.append(key)

# ========== Munsit ==========
MUNSIT_KEYS = []
for i in range(1, 10):
    key = os.getenv(f"MUNSIT_API_KEY{i}")
    if key:
        MUNSIT_KEYS.append(key)


        #   ================ content analyzer 
        from dotenv import load_dotenv
import os
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")



