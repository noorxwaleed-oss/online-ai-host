import os
import tempfile
import uuid
from typing import Optional

from fastapi import (
    FastAPI,
    Query,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Header,
)
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import cloudinary.api

try:
    import jwt  # PyJWT
except ImportError:
    jwt = None

from storage_services import (
    current_time,
    generate_id,
    list_user_projects,
    get_feed_url,
    get_project_metadata,
)
from utils import detect_input_type, parse_script_for_save


# =========================================================
# Auth dependency
# =========================================================

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")

# JWKS cache for asymmetric JWTs (ES256 / RS256). Supabase rotates rarely; 10 min TTL is fine.
import json as _json
import time as _time
import urllib.request as _urlreq
_jwks_cache: dict = {"keys": None, "fetched_at": 0.0}


def _fetch_jwks() -> Optional[dict]:
    if not SUPABASE_URL:
        return None
    if _jwks_cache["keys"] and (_time.time() - _jwks_cache["fetched_at"] < 600):
        return _jwks_cache["keys"]
    url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    try:
        with _urlreq.urlopen(url, timeout=5) as resp:
            data = _json.load(resp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch JWKS: {e}")
    _jwks_cache["keys"] = data
    _jwks_cache["fetched_at"] = _time.time()
    return data


def _public_key_from_jwks(alg: str, kid: Optional[str]):
    jwks = _fetch_jwks()
    if not jwks:
        raise HTTPException(
            status_code=500,
            detail="JWT uses asymmetric algorithm but SUPABASE_URL is not set on backend",
        )
    keys = jwks.get("keys") or []
    key_dict = None
    if kid:
        key_dict = next((k for k in keys if k.get("kid") == kid), None)
    if key_dict is None and keys:
        key_dict = keys[0]  # fallback to first key
    if not key_dict:
        raise HTTPException(status_code=401, detail="No matching JWKS key for token")

    from jwt.algorithms import ECAlgorithm, RSAAlgorithm  # requires pyjwt[crypto]
    serialized = _json.dumps(key_dict)
    if alg == "ES256":
        return ECAlgorithm.from_jwk(serialized)
    if alg in ("RS256", "RS384", "RS512"):
        return RSAAlgorithm.from_jwk(serialized)
    raise HTTPException(status_code=401, detail=f"Unsupported JWT algorithm: {alg}")


def get_current_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Verify the Supabase JWT in the Authorization header.

    Supports both legacy HS256 (with SUPABASE_JWT_SECRET) and current ES256/RS256
    (with SUPABASE_URL pointing at the project so JWKS can be fetched).

    Returns the user id (sub claim) on success.
    Returns None when neither SUPABASE_JWT_SECRET nor SUPABASE_URL is set
    (dev mode — auth not enforced).
    """
    auth_enabled = bool(SUPABASE_JWT_SECRET or SUPABASE_URL)
    if not auth_enabled:
        return None
    if jwt is None:
        raise HTTPException(
            status_code=500,
            detail="PyJWT not installed but auth is enabled",
        )
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()

    try:
        header = jwt.get_unverified_header(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Malformed token header: {e}")
    alg = (header or {}).get("alg", "HS256")
    kid = (header or {}).get("kid")

    try:
        if alg == "HS256":
            if not SUPABASE_JWT_SECRET:
                raise HTTPException(
                    status_code=500,
                    detail="Token uses HS256 but SUPABASE_JWT_SECRET is not set",
                )
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
        elif alg in ("ES256", "RS256", "RS384", "RS512"):
            public_key = _public_key_from_jwks(alg, kid)
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[alg],
                audience="authenticated",
            )
        else:
            raise HTTPException(status_code=401, detail=f"Unsupported JWT alg: {alg}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token has no subject")
    return sub


def require_owner(path_user_id: str, current_user_id: Optional[str]) -> None:
    """Reject if the JWT user does not match the user_id in the path/body."""
    if current_user_id is None:
        return  # auth not enforced
    if current_user_id != path_user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own projects",
        )


# =========================================================
# Uploaded-PDF temp storage
# =========================================================

PDF_TMP_DIR = os.path.join(tempfile.gettempdir(), "podcraft_pdf_uploads")
os.makedirs(PDF_TMP_DIR, exist_ok=True)



class multiAgent(BaseModel):
    host_name: str
    host_gender: str
    guest_name: str
    guest_gender: str
    podcast_name: str
    language: str
    content :str
    voice_id_host: str
    voice_id_guest: str
    host_style: str
    guest_style: str
    user_id: str 

app = FastAPI()

_cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "*")
_cors_origins = (
    ["*"] if _cors_origins_env.strip() == "*"
    else [o.strip() for o in _cors_origins_env.split(",") if o.strip()]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def get_podcast_details(host_name: str, host_gender: str, guest_name: str, guest_gender: str,
                        podcast_name: str, language: str, content: str , voice_id_host: str,
                          voice_id_guest: str , host_style: str, guest_style: str , user_id: str,
                          current_user_id: Optional[str] = Depends(get_current_user_id)):
    require_owner(user_id, current_user_id)
    try:

 #=====================================================
      # content_analyzer agnet 
      # user_id = generate_id()

    
      

      from content_analyzer import agent_analyzer
      from audio import generate_podcast_from_script
      import json
      from chat import textGeneration_chat_chain 
      key_points = agent_analyzer (content ,language)
      key_points_dict = json.loads(key_points)
      title = key_points_dict['topics'][0]['title']
  #=====================================================
      # text generation agent
      script = textGeneration_chat_chain.invoke({
          "key_points": key_points,
          "podcast_name": podcast_name,
          "host_name": host_name,
          "host_gender": host_gender,
          "guest_name": guest_name,
          "guest_gender": guest_gender,
      })

      from utils import tojson ,to_str_script
     
      json_script = tojson(script)
      script_str = to_str_script(json_script)
      # Script
      print(f"\n🎬 Generated Script:\n{script_str}")
  #=====================================================
    # store the script in Cloudinary and get the URL

      from storage_services import create_project, save_agent_output, save_input
      dic_script = parse_script_for_save(script_str)
      project = create_project(user_id) 
      project_id =  project["project_id"]  
      content_type = detect_input_type(content)
      if  content_type =='pdf':
          pdf_path = content
          source_url = None
      elif content_type =='url':
          pdf_path = None
          source_url =  content 
      else:
          print(" error unknown input : please enter url or pdf ")      
      save_input(user_id, project_id,content_type,pdf_path,source_url)
      savedscript = save_agent_output(user_id, project_id, "script",dic_script)
    
  #=====================================================
      #  audio generation agent
      provider = 'elevenlabs' if language.lower() == 'english' else 'munsit'
      lang = 'en' if language.lower() == 'english' else 'ar'
      
      # Host = Saudi Najdi male voice (Munsit)
      host_config = {
          'provider': provider,
          'language': lang,
          'gender':  host_gender,
          'style': host_style,
          'voice_id': voice_id_host
      }

      # Guest = Egyptian male voice (Munsit) — different voice
      # {"id": "ar-najdi-female-1", "name": "Maha", "gender": "female", "dialect": "saudi", "style": "calm"}
      guest_config = {
          'provider': provider,
          'language': lang,
          'gender': guest_gender,
          'style': guest_style,
          'voice_id': voice_id_guest
      }

      # Generate podcast
      result_audio = await generate_podcast_from_script(
          raw_text= script_str,
          host_config=host_config,
          guest_config=guest_config,
          speed=1.0,  # Normal speed
      )

      print(f"\n🎉 Final Result:")
      print(f"   Success: {result_audio.get('success')}")
      print(f"   Audio URL: {result_audio.get('audio_url')}")
      print(f"   Total duration: {result_audio.get('duration', 0):.2f} seconds")

      if result_audio.get('audio_url'):
          import requests
          from IPython.display import Audio, display
          response = requests.get(result_audio['audio_url'])
          # display(Audio(response.content))
      message = "Podcast generated successfully!" if result_audio.get('success') else "Failed to generate podcast."
      audio_output = {"message": message, "audio_url": result_audio.get('audio_url'), "duration": result_audio.get('duration', 0)}
      # return {"message": message, "audio_url": result_audio.get('audio_url'), "duration": result_audio.get('duration', 0)}


      #======================================================
      # save oudio agent
      from storage_services import save_audio_output
      save_audio_output(user_id, project_id, result_audio['audio_url']  )






      # ======================================================
      # COVER ART (non-fatal: if HF credits are out or the model errors,
      # we log it and continue — the user still gets the audio + script.)
      # ======================================================
      from cover_agent import CoverArtAgent
      from storage_services import save_cover_output

      coverArt_output = {"image_url": None}
      try:
          agent = CoverArtAgent()
          image = agent.generate(
              metadata=key_points_dict,
              style="Colorful",
              aspect_ratio="2:3"
          )
          # image.show() intentionally disabled — would open an image viewer
          # on the server, which is useless in production.
          coverArt_output = save_cover_output(user_id, project_id, image)
          print(f"Cover art saved: {coverArt_output.get('image_url')}")
      except Exception as cover_err:
          print(f"⚠️  Cover art generation failed: {cover_err}")
          print("   Continuing without cover art.")

      # ======================================================
      # PUBLISHING (also non-fatal: a missing cover or RSS hiccup
      # shouldn't hide the successfully-generated audio from the user.)
      # ======================================================
      try:
          from pub_models import EpisodeAssets, PodcastInfo, PublishingInput
          from publishing_agent import PublishingAgent
          from storage_services import get_feed_url, save_feed_url

          existing_feed = get_feed_url(user_id)
          cover_image_url = coverArt_output.get("image_url") or ""

          result = PublishingAgent().publish(
              PublishingInput(
                  episode=EpisodeAssets(
                      script_id=savedscript['public_id'],
                      title=title,
                      description=key_points_dict['topics'][0].get('insight', 'AI-generated podcast episode'),
                      audio_url=result_audio['audio_url'],
                      cover_image_url=cover_image_url,
                      duration_seconds=int(result_audio.get('duration', 0)),
                  ),
                  podcast=PodcastInfo(
                      podcast_title="AI Host Interview",
                      podcast_description="AI-generated podcast interviews on trending topics.",
                      author=user_id,
                      language="ar",
                      category="Technology",
                      cover_image_url=cover_image_url,
                  ),
                  existing_feed_url=existing_feed,
              ),
              user_id=user_id,
          )

          if result.success:
              save_feed_url(user_id, result.feed_url)
              print(f"Published! Feed URL: {result.feed_url}")
              print(f"Episodes in feed: {result.episode_count}")
          else:
              print(f"Publishing failed: {result.error_message}")
      except Exception as pub_err:
          print(f"⚠️  Publishing step failed: {pub_err}")
          print("   Continuing — the audio is already saved.")

      try:
          from storage_services import list_user_projects
          list_user_projects(user_id)
      except Exception:
          pass
  #======================================================
    #   # Retrieve and save metadata    
    #   from storage_services import get_project_metadata, save_metadata
    #   metadata =   get_project_metadata(user_id, project_id)
    #   saved_meatadata = save_metadata(metadata, user_id,  project_id)
    #   print(saved_meatadata)
      return audio_output
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
    





    # ========================================================


# =========================================================
# Read-only GET endpoints (additive — do not modify the
# generation flow above).
# =========================================================

def _find_first_resource(prefix: str, resource_type: str):
    """Return the secure_url of the first Cloudinary resource under prefix."""
    try:
        result = cloudinary.api.resources(
            type="upload",
            prefix=prefix,
            resource_type=resource_type,
            max_results=10,
        )
        resources = result.get("resources") or []
        if resources:
            return resources[0].get("secure_url")
    except Exception:
        return None
    return None


def _project_detail(user_id: str, project_id: str) -> dict:
    base = f"users/{user_id}/projects/{project_id}"

    metadata = None
    try:
        metadata = get_project_metadata(user_id, project_id)
    except Exception:
        metadata = None

    # Look up the RSS feed.xml directly via Cloudinary so we get the proper
    # versioned secure_url. storage_services.get_feed_url() constructs an
    # un-versioned URL that 404s for raw resources, so we don't use it here.
    feed_url = _find_first_resource(f"users/{user_id}/podcast", "raw")

    return {
        "user_id": user_id,
        "project_id": project_id,
        "metadata": metadata,
        "script_url": _find_first_resource(f"{base}/script", "raw"),
        "audio_url": _find_first_resource(f"{base}/audio_agent", "video"),
        "cover_url": _find_first_resource(f"{base}/cover_agent", "image"),
        "feed_url": feed_url,
    }


@app.get("/api/projects/{user_id}")
def api_list_projects(
    user_id: str,
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    require_owner(user_id, current_user_id)
    project_ids = list_user_projects(user_id)
    return {"user_id": user_id, "project_ids": project_ids}


@app.get("/api/projects/{user_id}/latest")
def api_latest_project(
    user_id: str,
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    require_owner(user_id, current_user_id)

    # Look up each project's `project.json` (created by storage_services.create_project)
    # and sort by Cloudinary's `created_at`. This is reliable; the previous logic
    # tried to fetch `metadata.json`, which create_project never writes, so it
    # always fell back to alphabetical order and returned a stale project.
    try:
        listing = cloudinary.api.resources(
            type="upload",
            prefix=f"users/{user_id}/projects",
            resource_type="raw",
            max_results=500,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary listing failed: {e}")

    latest_project_id = None
    latest_created_at = ""
    for res in listing.get("resources", []) or []:
        public_id = res.get("public_id", "")
        # Cloudinary stores raw files with their extension in public_id, so
        # storage_services.create_project produces:
        #   users/{user_id}/projects/{project_id}/project.json
        if not public_id.endswith("/project.json"):
            continue
        parts = public_id.split("/")
        # ['users', user_id, 'projects', project_id, 'project.json']
        if len(parts) < 5 or parts[0] != "users" or parts[2] != "projects":
            continue
        project_id = parts[3]
        created = res.get("created_at", "") or ""
        if created > latest_created_at:
            latest_created_at = created
            latest_project_id = project_id

    if not latest_project_id:
        raise HTTPException(status_code=404, detail="No projects found for user")

    return _project_detail(user_id, latest_project_id)


@app.get("/api/projects/{user_id}/{project_id}")
def api_get_project(
    user_id: str,
    project_id: str,
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    require_owner(user_id, current_user_id)
    return _project_detail(user_id, project_id)


@app.get("/api/feed/{user_id}")
def api_get_feed(
    user_id: str,
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    require_owner(user_id, current_user_id)
    feed_url = _find_first_resource(f"users/{user_id}/podcast", "raw")
    return {"user_id": user_id, "feed_url": feed_url}


@app.get("/api/health")
def api_health():
    return {
        "status": "ok",
        "time": current_time(),
        "auth_enforced": bool(SUPABASE_JWT_SECRET or SUPABASE_URL),
        "hs256_configured": bool(SUPABASE_JWT_SECRET),
        "jwks_configured": bool(SUPABASE_URL),
    }


# =========================================================
# PDF Upload (multipart)
# =========================================================

MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB


@app.post("/api/upload-pdf")
async def api_upload_pdf(
    file: UploadFile = File(...),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """
    Accept a PDF upload and persist it to a server-local temp file.

    Returns a 'content' string the client should pass straight through to
    POST / — the existing generation flow detects it as a local PDF file
    via os.path.isfile() in utils.detect_input_type.
    """
    if SUPABASE_JWT_SECRET and current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Stream-read with a size cap
    data = await file.read(MAX_PDF_BYTES + 1)
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    user_dir = os.path.join(PDF_TMP_DIR, current_user_id or "anon")
    os.makedirs(user_dir, exist_ok=True)
    local_path = os.path.join(user_dir, f"{uuid.uuid4().hex}.pdf")
    with open(local_path, "wb") as f:
        f.write(data)

    return {
        "content": local_path,
        "size": len(data),
        "filename": file.filename,
    }


# =========================================================
# Voice preview
# =========================================================

class VoicePreviewRequest(BaseModel):
    voice_id: str
    language: str = "english"          # "english" | "arabic"
    gender: str = "male"               # "male" | "female"
    style: str = "professional"
    dialect: Optional[str] = None      # only relevant for Arabic

# In-memory cache: voice_id -> audio_url. Sample text is fixed so the URL is
# stable per voice and re-uploading on every click would be wasteful.
_voice_preview_cache: dict[str, str] = {}

_PREVIEW_SAMPLE_EN = "Hello, this is a short preview of my voice."
_PREVIEW_SAMPLE_AR = "مرحبا، هذه معاينة قصيرة لصوتي."


@app.post("/api/voice-preview")
async def api_voice_preview(
    payload: VoicePreviewRequest,
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    if SUPABASE_JWT_SECRET and current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    if payload.voice_id in _voice_preview_cache:
        return {"audio_url": _voice_preview_cache[payload.voice_id], "cached": True}

    lang_norm = payload.language.lower()
    is_arabic = lang_norm.startswith("ar")
    text = _PREVIEW_SAMPLE_AR if is_arabic else _PREVIEW_SAMPLE_EN
    provider = "munsit" if is_arabic else "elevenlabs"
    lang_code = "ar" if is_arabic else "en"

    # Import lazily so app boot doesn't fail if audio deps are missing
    try:
        from audio import text_to_speech
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio module unavailable: {e}")

    try:
        result = await text_to_speech(
            text=text,
            provider=provider,
            language=lang_code,
            dialect=payload.dialect or "fusha",
            gender=payload.gender,
            style=payload.style,
            speed=1.0,
            voice_id=payload.voice_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

    if not result.get("success") or not result.get("audio_url"):
        raise HTTPException(
            status_code=502,
            detail=result.get("error") or "TTS provider returned no audio",
        )

    audio_url = result["audio_url"]
    _voice_preview_cache[payload.voice_id] = audio_url
    return {"audio_url": audio_url, "cached": False}
