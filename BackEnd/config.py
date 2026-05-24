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
elevenlabs_api_key4 = os.getenv("ELEVENLABS_API_KEY4")
munsit_api_key1 = os.getenv("MUNSIT_API_KEY1")
munsit_api_key2 = os.getenv("MUNSIT_API_KEY2")
munsit_api_key3 = os.getenv("MUNSIT_API_KEY3")
HF_token_coverArt = os.getenv("HF_TOKEN_coverArt")


cloudinary_config =  cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


# ELEVENLABS_KEYS = []
# for i in range(1, 10):
#     key = os.getenv(f"ELEVENLABS_API_KEY{i}")
#     if key:
#         ELEVENLABS_KEYS.append(key)

# # ========== Munsit ==========
# MUNSIT_KEYS = []
# for i in range(1, 10):
#     key = os.getenv(f"MUNSIT_API_KEY{i}")
#     if key:
#         MUNSIT_KEYS.append(key)


#         #   ================ content analyzer 
#         from dotenv import load_dotenv
# import os
# load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
"""Centralized configuration for the Audio Production Agent."""

import os
from dotenv import load_dotenv

load_dotenv()

# ========== Cloudinary ==========
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# ========== ElevenLabs ==========
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





MODEL = "Tongyi-MAI/Z-Image-Turbo"



# =========================
# IMAGE SIZES
# =========================

ASPECT_RATIOS = {
    "1:1": (768, 768),
    "16:9": (1024, 576),
    "4:5": (768, 960),
    "2:3": (768, 1152)
}
