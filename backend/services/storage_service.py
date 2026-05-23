import cloudinary.uploader
import cloudinary.api
import json
import os
import tempfile
import uuid
import requests
from datetime import datetime
from backend.config.settings import settings
from backend.cloudinary.config import cloudinary_config

def generate_id() -> str:
    return str(uuid.uuid4())

def current_time() -> str:
    return datetime.utcnow().isoformat()

def build_project_folder(user_id: str, project_id: str) -> str:
    return f"users/{user_id}/projects/{project_id}"

def _upload_json(data: dict, folder: str, public_id: str) -> dict:
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as temp_file:
        temp_file.write(json_str)
        temp_path = temp_file.name
    try:
        result = cloudinary.uploader.upload(
            temp_path,
            resource_type="raw",
            folder=folder,
            public_id=public_id,
            overwrite=True
        )
        return result
    except Exception as e:
        raise RuntimeError(f"Cloudinary JSON upload failed: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def create_project(user_id: str) -> dict:
    project_id = generate_id()
    project_folder = build_project_folder(user_id=user_id, project_id=project_id)
    project_data = {
        "project_id": project_id,
        "user_id": user_id,
        "status": "created",
        "created_at": current_time(),
        "updated_at": current_time(),
        "folder": project_folder
    }
    _upload_json(data=project_data, folder=project_folder, public_id="project")
    return project_data

def update_project_status(user_id: str, project_id: str, status: str) -> dict:
    metadata = get_project_metadata(user_id=user_id, project_id=project_id)
    metadata["status"] = status
    metadata["updated_at"] = current_time()
    result = _upload_json(data=metadata, folder=build_project_folder(user_id, project_id), public_id="metadata")
    return {"status": status, "metadata_url": result["secure_url"]}

def save_input(user_id: str, project_id: str, input_type: str, pdf_path: str = None, source_url: str = None) -> dict:
    input_folder = f"{build_project_folder(user_id, project_id)}/input"
    input_data = {
        "input_id": generate_id(),
        "type": input_type,
        "pdf_url": None,
        "source_url": None,
        "created_at": current_time()
    }
    if input_type == "pdf":
        if not pdf_path:
            raise ValueError("pdf_path is required for PDF input")
        result = cloudinary.uploader.upload(pdf_path, resource_type="raw", folder=input_folder, public_id="source_pdf", overwrite=True)
        input_data["pdf_url"] = result["secure_url"]
    elif input_type == "url":
        if not source_url:
            raise ValueError("source_url is required for URL input")
        input_data["source_url"] = source_url
    else:
        raise ValueError("input_type must be either 'pdf' or 'url'")
    _upload_json(data=input_data, folder=input_folder, public_id="input_metadata")
    return input_data

def save_agent_output(user_id: str, project_id: str, agent_name: str, data: dict) -> dict:
    folder = f"{build_project_folder(user_id, project_id)}/{agent_name}"
    result = _upload_json(data=data, folder=folder, public_id="output")
    return {"agent": agent_name, "url": result["secure_url"], "public_id": result["public_id"]}

def save_audio_output(user_id: str, project_id: str, audio_path: str) -> dict:
    folder = f"{build_project_folder(user_id, project_id)}/audio_agent"
    result = cloudinary.uploader.upload(audio_path, resource_type="video", folder=folder, public_id="output_audio", overwrite=True)
    return {"audio_url": result["secure_url"], "public_id": result["public_id"]}

def save_cover_output(user_id: str, project_id: str, image) -> dict:
    folder = f"{build_project_folder(user_id, project_id)}/cover_agent"
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        image.save(tmp.name, format="PNG")
        temp_path = tmp.name
    result = cloudinary.uploader.upload(temp_path, folder=folder, public_id="cover_image", overwrite=True, resource_type="image")
    if os.path.exists(temp_path):
        os.remove(temp_path)
    return {"image_url": result["secure_url"], "public_id": result["public_id"]}

def save_feed_url(user_id: str, feed_url: str) -> dict:
    result = _upload_json(data={"feed_url": feed_url, "updated_at": current_time()}, folder=f"users/{user_id}", public_id="feed_info")
    return {"feed_url": feed_url, "url": result["secure_url"]}

def get_feed_url(user_id: str) -> str | None:
    url = f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/raw/upload/users/{user_id}/feed_info.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("feed_url")
        return None
    except Exception:
        return None

def list_user_projects(user_id: str) -> list:
    try:
        result = cloudinary.api.subfolders(f"users/{user_id}/projects")
        return [folder["name"] for folder in result["folders"]]
    except Exception:
        return []

def get_project_metadata(user_id: str, project_id: str) -> dict:
    url = f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/raw/upload/users/{user_id}/projects/{project_id}/metadata.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve project metadata: {e}")
