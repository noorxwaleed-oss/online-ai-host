import cloudinary.uploader
import cloudinary.api
import json
import os
import tempfile
import uuid
import requests
from datetime import datetime
from config import CLOUDINARY_CLOUD_NAME


# =========================================================
# Helper Functions
# =========================================================

def generate_id() -> str:
    """
    Generate a unique UUID string.

    Returns:
        str: Unique identifier.
    """
    return str(uuid.uuid4())


def current_time() -> str:
    """
    Get current UTC timestamp.

    Returns:
        str: ISO formatted UTC datetime.
    """
    return datetime.utcnow().isoformat()


def build_project_folder(user_id: str, project_id: str) -> str:
    """
    Build the Cloudinary folder path for a project.

    Args:
        user_id (str): User identifier.
        project_id (str): Project identifier.

    Returns:
        str: Full project folder path.
    """
    return f"users/{user_id}/projects/{project_id}"


# =========================================================
# Core Upload Helper
# =========================================================

def _upload_json(data: dict, folder: str, public_id: str) -> dict:
    """
    Upload a dictionary as a JSON file to Cloudinary.

    Args:
        data (dict): Data to upload.
        folder (str): Cloudinary folder path.
        public_id (str): File public ID.

    Returns:
        dict: Cloudinary upload response.

    Raises:
        RuntimeError: If upload fails.
    """

    json_str = json.dumps(data, indent=2 , ensure_ascii=False)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8"
    ) as temp_file:

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

        raise RuntimeError(
            f"Cloudinary JSON upload failed: {e}"
        )

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# =========================================================
# Project Management
# =========================================================

def create_project(user_id: str) -> dict:
    """
    Create a new project structure in Cloudinary.

    Args:
        user_id (str): User identifier.

    Returns:
        dict: Created project metadata.

    Raises:
        RuntimeError: If project creation fails.
    """

    project_id = generate_id()

    project_folder = build_project_folder(
        user_id=user_id,
        project_id=project_id
    )

    project_data = {
        "project_id": project_id,
        "user_id": user_id,
        "status": "created",
        "created_at": current_time(),
        "updated_at": current_time(),
        "folder": project_folder
    }

    try:

        _upload_json(
            data=project_data,
            folder=project_folder,
            public_id="project"
        )

        return project_data

    except Exception as e:

        raise RuntimeError(
            f"Project creation failed: {e}"
        )


# =========================================================
# Project Status Management
# =========================================================

def update_project_status(
    user_id: str,
    project_id: str,
    status: str
) -> dict:
    """
    Update project processing status.

    Args:
        user_id (str): User identifier.
        project_id (str): Project identifier.
        status (str): New project status.

    Returns:
        dict: Updated status information.
    """

    metadata = get_project_metadata(
        user_id=user_id,
        project_id=project_id
    )

    metadata["status"] = status
    metadata["updated_at"] = current_time()

    result = _upload_json(
        data=metadata,
        folder=build_project_folder(user_id, project_id),
        public_id="metadata"
    )

    return {
        "status": status,
        "metadata_url": result["secure_url"]
    }


# =========================================================
# Input Management
# =========================================================

def save_input(
    user_id: str,
    project_id: str,
    input_type: str,
    pdf_path: str = None,
    source_url: str = None
) -> dict:
    """
    Save project input data.

    Supports:
    - PDF uploads
    - Source URLs

    Args:
        user_id (str): User identifier.
        project_id (str): Project identifier.
        input_type (str): "pdf" or "url"
        pdf_path (str): Local PDF path
        source_url (str): Website/article URL

    Returns:
        dict: Saved input metadata.

    Raises:
        RuntimeError: If saving fails.
    """

    input_folder = (
        f"{build_project_folder(user_id, project_id)}/input"
    )

    input_data = {
        "input_id": generate_id(),
        "type": input_type,
        "pdf_url": None,
        "source_url": None,
        "created_at": current_time()
    }

    try:

        # =================================================
        # PDF Upload
        # =================================================
        if input_type == "pdf":

            if not pdf_path:
                raise ValueError(
                    "pdf_path is required for PDF input"
                )

            result = cloudinary.uploader.upload(
                pdf_path,
                resource_type="raw",
                folder=input_folder,
                public_id="source_pdf",
                overwrite=True
            )

            input_data["pdf_url"] = result["secure_url"]

        # =================================================
        # URL Save
        # =================================================
        elif input_type == "url":

            if not source_url:
                raise ValueError(
                    "source_url is required for URL input"
                )

            input_data["source_url"] = source_url

        else:
            raise ValueError(
                "input_type must be either 'pdf' or 'url'"
            )

        # =================================================
        # Save Metadata
        # =================================================
        _upload_json(
            data=input_data,
            folder=input_folder,
            public_id="input_metadata"
        )

        return input_data

    except Exception as e:

        raise RuntimeError(
            f"Input saving failed: {e}"
        )


# =========================================================
# Agent Output Storage
# =========================================================

def save_agent_output(
    user_id: str,
    project_id: str,
    agent_name: str,
    data: dict
) -> dict:
    """
    Save any agent output as JSON.

    Each agent has its own folder inside the project.

    Example folders:
    - analyzer_agent/
    - script_agent/
  

    Args:
        user_id (str): User identifier.
        project_id (str): Project identifier.
        agent_name (str): Agent folder name.
        data (dict): Agent output data.

    Returns:
        dict: Upload metadata.
    """

    folder = (
        f"{build_project_folder(user_id, project_id)}/{agent_name}"
    )

    result = _upload_json(
        data=data,
        folder=folder,
        public_id="output"
    )

    return {
        "agent": agent_name,
        "url": result["secure_url"],
        "public_id": result["public_id"]
    }


# =========================================================
# Audio Storage
# =========================================================

def save_audio_output(user_id, project_id, audio_path):
    folder = f"{build_project_folder(user_id, project_id)}/audio_agent"

    result = cloudinary.uploader.upload(
        audio_path,
        resource_type="video",  # Cloudinary treats audio as video
        folder=folder,
        public_id="output_audio",
        overwrite=True
    )

    return {
        "audio_url": result["secure_url"],
        "public_id": result["public_id"]
    }

# =========================================================
# Cover Image Storage

import cloudinary.uploader
import tempfile

def save_cover_output(user_id, project_id, image):
    folder = f"users/{user_id}/projects/{project_id}/cover_agent"

    # save PIL image to temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        image.save(tmp.name, format="PNG")
        temp_path = tmp.name

    result = cloudinary.uploader.upload(
        temp_path,
        folder=folder,
        public_id="cover_image",
        overwrite=True,
        resource_type="image"
    )

    return {
        "image_url": result["secure_url"],
        "public_id": result["public_id"]
    }

# =========================================================
# Feed Management
# =========================================================

def save_feed_url(user_id: str, feed_url: str) -> dict:
    """
    Save RSS feed URL for a user.

    Args:
        user_id (str): User identifier.
        feed_url (str): RSS feed URL.

    Returns:
        dict: Saved feed information.
    """

    result = _upload_json(
        data={
            "feed_url": feed_url,
            "updated_at": current_time()
        },
        folder=f"users/{user_id}",
        public_id="feed_info"
    )

    return {
        "feed_url": feed_url,
        "url": result["secure_url"]
    }


def get_feed_url(user_id: str) -> str | None:
    """
    Retrieve saved RSS feed URL.

    Args:
        user_id (str): User identifier.

    Returns:
        str | None: Feed URL if exists.
    """

    url = (
        f"https://res.cloudinary.com/"
        f"{CLOUDINARY_CLOUD_NAME}/raw/upload/"
        f"users/{user_id}/feed_info.json"
    )

    try:

        response = requests.get(url)

        if response.status_code == 200:
            return response.json().get("feed_url")

        return None

    except Exception:
        return None


# =========================================================
# Project Retrieval
# =========================================================

def list_user_projects(user_id: str) -> list:
    """
    List all user project IDs.

    Args:
        user_id (str): User identifier.

    Returns:
        list: List of project IDs.
    """

    try:

        result = cloudinary.api.subfolders(
            f"users/{user_id}/projects"
        )

        return [
            folder["name"]
            for folder in result["folders"]
        ]

    except cloudinary.api.NotFound:
        return []

    except Exception:
        return []


def get_project_metadata(
    user_id: str,
    project_id: str
) -> dict:
    """
    Retrieve project metadata JSON.

    Args:
        user_id (str): User identifier.
        project_id (str): Project identifier.

    Returns:
        dict: Project metadata.

    Raises:
        RuntimeError: If retrieval fails.
    """

    url = (
        f"https://res.cloudinary.com/"
        f"{CLOUDINARY_CLOUD_NAME}/raw/upload/"
        f"users/{user_id}/projects/"
        f"{project_id}/metadata.json"
    )

    try:

        response = requests.get(url)

        response.raise_for_status()

        return response.json()

    except Exception as e:

        raise RuntimeError(
            f"Failed to retrieve project metadata: {e}"
        )