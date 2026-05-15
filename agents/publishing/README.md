# Publishing Agent — v1.0 (Mocked)

The final agent in the AI Host Interview pipeline. Takes approved assets
(script, audio, cover) and routes them to platform-specific publishers.

**Owner:** Maryam · **Status:** v1.0 — all adapters mocked

---

## What it does

Given a `PublishingInput` containing approved assets + a list of target
platforms + the user's connected accounts, the Publishing Agent:

1. Validates that the user has connected each targeted platform
2. Dispatches to platform-specific adapters (one per platform)
3. Aggregates per-platform results into a single `PublishingOutput`
4. Writes an audit log entry for each successful publish

## What it does NOT do (v1.0 limitations)

- Does not make real API calls. All adapters are mocked.
- Does not handle OAuth flows or credential storage.
- Does not retry on failure (real implementation would; mocks don't fail).
- Does not handle scheduled publishing.

These are explicit graduation-scope choices, not oversights. The architecture
supports each of these as drop-in additions: replace one mock adapter at a
time, add a credential vault behind the `is_connected` check.

---

## Why mocking is the right call for graduation

Real publishing requires:
- Spotify for Podcasters API integration + RSS feed hosting
- Anghami API integration + content licensing
- YouTube Music / YouTube Data API + OAuth 2.0 flow
- Apple Podcasts Connect API + RSS feed submission

These are 3-4 weeks of work that doesn't demonstrate any new architectural
or AI capability. The intelligent design lives in the adapter pattern, the
audit logging, the credential isolation, and the integration contract —
all of which can be demonstrated with mocks.

---

## Project structure

```
publishing_agent/
├── .example.env               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── base.py                    # PublishingAdapter Protocol
├── chat.py                    # Chain wiring
├── config.py                  # Centralized configuration
├── mock_adapters.py           # Spotify, Anghami, YouTube Music, Apple Podcasts
├── models.py                  # Pydantic I/O contract
├── publishing_agent.py        # Main PublishingAgent class
├── quickstart.py              # End-to-end demo
├── test_publishing.py         # 9 unit tests
└── utils.py                   # Utility helpers
```

---

## Setup

```bash
pip install pydantic
```

That's it. No API keys needed; all adapters are mocked.

## Run tests

```bash
cd publishing_agent
python test_publishing.py
```

Should print 9 passed, 0 failed.

## Run the demo

```bash
python quickstart.py
```

Publishes a sample episode to all four mock platforms and prints results.

---

## Architecture: Adapter pattern

The agent does not know which platforms exist. It dispatches to whatever
adapters are registered. Adding a new platform = creating a new adapter file.
Replacing a mock with a real implementation = swapping one file, no agent
code changes.

```
PublishingAgent
    |
    +-- SpotifyAdapter        (podcast/music streaming)
    +-- AnghamiAdapter        (Middle Eastern streaming)
    +-- YouTubeMusicAdapter   (YouTube Music)
    +-- ApplePodcastsAdapter  (Apple Podcasts)
```

Every adapter implements `PublishingAdapter` (a Python `Protocol`):

```python
class PublishingAdapter(Protocol):
    platform: Platform
    def publish(self, assets, user_id) -> PlatformResult: ...
    def is_connected(self, user_id) -> bool: ...
```

To swap mocks for real adapters in production:

```python
real_adapters = {
    Platform.SPOTIFY: RealSpotifyAdapter(oauth_client),
    Platform.ANGHAMI: RealAnghamiAdapter(api_key),
    Platform.YOUTUBE_MUSIC: RealYouTubeMusicAdapter(oauth_client),
    Platform.APPLE_PODCASTS: RealApplePodcastsAdapter(api_key),
}
agent = PublishingAgent(adapters=real_adapters)
```

---

## Integration with the team

The Publishing Agent is called by Asmaa's Orchestrator, **after** the script
has been approved by the Critic, the audio has been produced by Aya, and the
cover art has been designed by Nour. It's the final step in the pipeline.

| Field                       | Source agent                    |
|-----------------------------|---------------------------------|
| `assets.script_id`          | Aliaa (Scriptwriter)            |
| `assets.audio_file_path`    | Aya (Audio Production)          |
| `assets.cover_image_path`   | Nour (Cover Design)             |
| `assets.title, description` | Generated from the approved script |
| `user.user_id`              | Asmaa (from session)            |
| `user.connected_platforms`  | Asmaa (from credential DB)      |
| `target_platforms`          | User's choice via UI            |

---

## Audit log

Every successful publish writes one JSON object per line to `audit_log.jsonl`:

```json
{
  "platform": "spotify",
  "user_id": "demo_user",
  "script_id": "scr_demo_001",
  "title": "The Rise of Foldable Phones in 2026",
  "platform_post_id": "spot_d328bd4fdd",
  "url": "https://mock-spotify.com/episode/spot_d328bd4fdd",
  "timestamp": "2026-05-03T18:39:49.131719+00:00"
}
```

This satisfies Milestone 4's monitoring requirement and gives the user
a permanent record of where their content was published.
