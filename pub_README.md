# Publishing Agent — v3.0 (RSS Feed)

The final agent in the AI Host Interview pipeline. Generates and maintains
a podcast RSS feed on Cloudinary. All major platforms (Spotify, Anghami,
Apple Podcasts, YouTube Music) auto-pull new episodes from this feed.

**Owner:** Maryam · **Status:** v3.0

---

## How it works

1. **First episode:** Agent creates an RSS XML feed → uploads to Cloudinary → returns feed URL
2. **New episodes:** Agent fetches existing feed → prepends new episode → re-uploads
3. **User submits the feed URL once** to each platform dashboard
4. **Every new episode auto-appears** on all platforms — no manual action needed

---

## Project structure

```
publishing_agent/
├── .example.env               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── chat.py                    # Chain wiring
├── config.py                  # Cloudinary configuration
├── models.py                  # Pydantic I/O contract (v3.0)
├── publishing_agent.py        # Main PublishingAgent class
├── quickstart.py              # End-to-end demo
├── rss_builder.py             # RSS XML generation and update
├── test_publishing.py         # 11 unit tests
└── utils.py                   # Utility helpers
```

---

## Setup

```bash
pip install pydantic requests cloudinary
```

Copy `.example.env` to `.env` and fill in Cloudinary credentials.

## Run tests (no Cloudinary needed)

```bash
cd publishing_agent
python test_publishing.py
```

Should print 11 passed, 0 failed.

## Run the demo (no Cloudinary needed for XML preview)

```bash
python quickstart.py
```

---

## Integration with the pipeline

```python
from publishing_agent import PublishingAgent
from models import PublishingInput, EpisodeAssets, PodcastInfo

agent = PublishingAgent()

result = agent.publish(PublishingInput(
    episode=EpisodeAssets(
        script_id=script_result["public_id"],
        title=analysis["title"],
        description=analysis["summary"],
        audio_url=audio["audio_url"],
        cover_image_url=cover["cover_url"],
        duration_seconds=audio["duration"],
    ),
    podcast=PodcastInfo(
        podcast_title="My AI Podcast",
        podcast_description="Auto-generated interviews",
        author="User Name",
        language="ar",
        category="Technology",
        cover_image_url=cover["podcast_cover_url"],
    ),
    existing_feed_url=previous_feed_url,  # None for first episode
))

# result.feed_url → Cloudinary URL of the RSS feed
# User submits this URL once to Spotify/Anghami/Apple/YouTube
```

---

## Where the user submits the feed URL

| Platform       | Dashboard URL                              |
|----------------|--------------------------------------------|
| Spotify        | https://podcasters.spotify.com             |
| Anghami        | https://anghami.com/podcasters             |
| Apple Podcasts | https://podcastsconnect.apple.com          |
| YouTube Music  | https://music.youtube.com/podcasts         |

---

## RSS Feed example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>AI Host Interview</title>
    <description>AI-generated podcast interviews</description>
    <language>ar</language>
    <itunes:author>Online AI Host Team</itunes:author>
    <item>
      <title>Episode 1: Foldable Phones</title>
      <enclosure url="https://cloudinary.com/ep1.mp3" type="audio/mpeg"/>
      <guid isPermaLink="false">scr_001</guid>
    </item>
  </channel>
</rss>
```
