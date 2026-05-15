
import json
def tojson (text):
    
  data = json.loads(text.content)
  
  return data

def print_script(script):


  # print(json.dumps(script, indent=4, ensure_ascii=False))
  print(script["total_pages"])
  for page in script["pages"]:
      print(f"Page {page['page_number']}:")
      print(page["content"])
      print("\n---\n")




  """Utility helpers for the Audio Production Agent."""

import os
import uuid
from typing import Dict, Any

import cloudinary
import cloudinary.uploader

# from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET


# # Configure Cloudinary
# cloudinary.config(
#     cloud_name=CLOUDINARY_CLOUD_NAME,
#     api_key=CLOUDINARY_API_KEY,
#     api_secret=CLOUDINARY_API_SECRET,
# )


def upload_to_cloudinary(audio_bytes: bytes, file_ext: str = '.mp3') -> Dict[str, Any]:
    """Upload audio bytes to Cloudinary and return URL + duration."""
    filename = f"temp_audio_{uuid.uuid4()}{file_ext}"

    with open(filename, 'wb') as f:
        f.write(audio_bytes)

    try:
        upload_result = cloudinary.uploader.upload(
            filename,
            folder="podcast_audio",
            resource_type="auto",
        )
        return {
            'success': True,
            'url': upload_result.get('secure_url'),
            'duration': upload_result.get('duration', 0),
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        if os.path.exists(filename):
            os.remove(filename)





import bs4
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader

def load_data(source):
    if source.startswith("http"):
        loader = WebBaseLoader(
            web_path=(source,),
            bs_kwargs=dict(parse_only=bs4.SoupStrainer(name=("article", "h1", "h2", "h3", "p")))
        )
    else:
        loader = PyPDFLoader(source)
    return loader.load()
