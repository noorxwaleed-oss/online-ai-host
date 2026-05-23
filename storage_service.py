import cloudinary.uploader
import cloudinary.api
import json
import os
import tempfile
import uuid
import requests
from config import CLOUDINARY_CLOUD_NAME


def _upload_json(data: dict, folder: str, public_id: str) -> dict:
    """Helper to upload a dict as a JSON file to Cloudinary."""
    json_str = json.dumps(data)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(json_str)
        temp_path = f.name

    try:
        result = cloudinary.uploader.upload(
            temp_path,
            resource_type="raw",
            folder=folder,
            public_id=public_id,
        )
        return result
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed for {folder}/{public_id}: {e}")
    finally:
        os.unlink(temp_path)


def create_project(user_id: str) -> dict:
    """Create a new project folder on Cloudinary."""
    project_id = str(uuid.uuid4())
    print(f"Creating project {project_id} for user {user_id}...")
    project_data = {
        "user_id": user_id,
        "project_id": project_id,
        "folder": f"users/{user_id}/projects/{project_id}",
        "status": "created",
    }

    try:
        _upload_json(
            project_data,
            folder=f"users/{user_id}/projects/{project_id}",
            public_id="project",
        )
        return project_data
    except Exception as e:
        raise RuntimeError(f"Failed to create project: {e}")

    return project_data


def save_input(user_id: str, project_id: str, input_type: str,
               pdf_path: str = None, source_url: str = None) -> dict:
    """Upload the source input (PDF or URL) to Cloudinary."""
    input_data = {
        "id": str(uuid.uuid4()),
        "type": input_type,
        "source_url": source_url,
        "pdf_url": None,
    }

    if input_type == "pdf" and pdf_path:
        try:
            result = cloudinary.uploader.upload(
                pdf_path,
                resource_type="raw",
                folder=f"users/{user_id}/projects/{project_id}/input",
                public_id="source_pdf",
            )
            input_data["pdf_url"] = result["secure_url"]
        except Exception as e:
            raise RuntimeError(f"Failed to upload PDF: {e}")

    return input_data


def save_script(script_json: dict, user_id: str, project_id: str) -> dict:
    """Upload the generated script JSON to Cloudinary."""
    result = _upload_json(
        script_json,
        folder=f"users/{user_id}/projects/{project_id}/scripts",
        public_id="script",
    )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
    }


def save_metadata(metadata: dict, user_id: str, project_id: str) -> dict:
    """Upload the full pipeline metadata to Cloudinary."""
    result = _upload_json(
        metadata,
        folder=f"users/{user_id}/projects/{project_id}",
        public_id="metadata",
    )

    return {
        "metadata_url": result["secure_url"],
        "public_id": result["public_id"],
    }


def save_feed_url(user_id: str, feed_url: str) -> dict:
    """Save the user's RSS feed URL so subsequent episodes can update it."""
    result = _upload_json(
        {"feed_url": feed_url},
        folder=f"users/{user_id}",
        public_id="feed_info",
    )
    print(f"Feed URL saved for user {user_id}: {result['secure_url']}")
    return {"url": result["secure_url"]}


def get_feed_url(user_id: str) -> str | None:
    """Retrieve the user's existing RSS feed URL. Returns None if no feed exists."""
    url = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/raw/upload/users/{user_id}/feed_info.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("feed_url")
        return None
    except Exception:
        return None


def list_user_projects(user_id: str) -> list:
    """Return all project IDs for a given user."""
    try:
        result = cloudinary.api.subfolders(f"users/{user_id}/projects")
        return [f["name"] for f in result["folders"]]
    except cloudinary.api.NotFound:
        return []
    except Exception:
        return []


def get_project_metadata(user_id: str, project_id: str) -> dict:
    """Fetch a project's metadata.json from Cloudinary."""
    url = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/raw/upload/users/{user_id}/projects/{project_id}/metadata.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch metadata for project {project_id}: {e}")
