# Online AI Host — Pipeline

The main orchestration layer for the AI Host Interview project. Runs all agents in sequence and manages storage on Cloudinary.

---

## Project structure

```
pipeline/
├── .env                       # Cloudinary credentials (not committed)
├── config.py                  # Cloudinary initialization + validation
├── main.py                    # Pipeline orchestration (runs all agents)
├── storage_service.py         # Cloudinary storage layer
└── README.md                  # This file
```

---

## Setup

```bash
pip install cloudinary python-dotenv requests
```

Create a `.env` file:

```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

## How it works

`main.py` runs the full pipeline for a given user:

1. **Create project** — creates a folder on Cloudinary under `users/{user_id}/projects/{project_id}/`
2. **Save input** — uploads the source PDF to Cloudinary
3. **Content Analysis Agent** — extracts key points from the source
4. **Text Generation Agent** — generates a podcast script from key points
5. **Save script** — uploads the script JSON to Cloudinary
6. **Audio Production Agent** — converts the script to audio (MP3 on Cloudinary)
7. **Publishing Agent** — generates/updates an RSS feed on Cloudinary
8. **Save metadata** — uploads the full pipeline metadata to Cloudinary

---

## File details

### `config.py`

Loads Cloudinary credentials from `.env` and validates they exist. Crashes early with a clear error if any are missing. Every other file imports `config` to initialize Cloudinary.

### `storage_service.py`

All Cloudinary interactions go through this file. Functions:

- `create_project(user_id)` — creates a project folder, returns `project_id`
- `save_input(user_id, project_id, input_type, pdf_path)` — uploads source PDF
- `save_script(script_json, user_id, project_id)` — uploads generated script
- `save_metadata(metadata, user_id, project_id)` — uploads full pipeline metadata
- `save_feed_url(user_id, feed_url)` — persists the RSS feed URL for the user
- `get_feed_url(user_id)` — retrieves existing feed URL (returns `None` for first episode)
- `list_user_projects(user_id)` — lists all project IDs for a user
- `get_project_metadata(user_id, project_id)` — fetches a project's metadata

### `main.py`

Orchestrates the full pipeline. Agent calls are currently placeholder comments — uncomment and adjust imports as each agent is integrated.

---

## Cloudinary folder structure

```
users/
└── {user_id}/
    ├── feed_info.json                          # RSS feed URL for this user
    └── projects/
        └── {project_id}/
            ├── project.json                    # Project metadata
            ├── metadata.json                   # Full pipeline output
            ├── input/
            │   └── source_pdf                  # Uploaded PDF
            └── scripts/
                └── script.json                 # Generated script
```

---

## Running

```bash
python main.py
```

Currently runs with placeholder data. As agents are integrated, uncomment the imports and agent calls in `main.py`.

---

## Integration with agents

Each agent is imported from its own folder under `agents/`:

| Step | Agent | Folder | Input | Output |
|------|-------|--------|-------|--------|
| 1 | Content Analyzer | `agents/content_analyzer/` | PDF URL | key_points, title, summary |
| 2 | Text Generation | `agents/text_generation/` | key_points, tone, speed | script (Host/Guest turns) |
| 3 | Audio Production | `agents/audio/` | script text | Cloudinary audio URL |
| 4 | Publishing | `agents/publishing/` | episode assets, podcast info | RSS feed URL |
