"""
RSS feed builder for the Publishing Agent.

Generates a valid podcast RSS 2.0 feed with iTunes extensions.
Platforms (Spotify, Anghami, Apple Podcasts, YouTube Music) auto-pull
new episodes from this feed.

RSS 2.0 spec: https://www.rssboard.org/rss-specification
iTunes extensions: https://podcasters.apple.com/support/823-podcast-requirements
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from typing import Optional

from pub_models import EpisodeAssets, PodcastInfo


# iTunes namespace
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def create_new_feed(podcast: PodcastInfo, episode: EpisodeAssets) -> str:
    """Create a brand new RSS feed with one episode. Returns XML string."""

    # Register iTunes namespace
    ET.register_namespace("itunes", ITUNES_NS)

    rss = ET.Element("rss", attrib={
        "version": "2.0",
    })

    channel = ET.SubElement(rss, "channel")

    # Podcast-level metadata
    ET.SubElement(channel, "title").text = podcast.podcast_title
    ET.SubElement(channel, "description").text = podcast.podcast_description
    ET.SubElement(channel, "language").text = podcast.language
    ET.SubElement(channel, "link").text = podcast.cover_image_url
    ET.SubElement(channel, f"{{{ITUNES_NS}}}author").text = podcast.author
    ET.SubElement(channel, f"{{{ITUNES_NS}}}summary").text = podcast.podcast_description
    ET.SubElement(channel, f"{{{ITUNES_NS}}}category", attrib={"text": podcast.category})
    ET.SubElement(channel, f"{{{ITUNES_NS}}}explicit").text = "false"

    # Podcast cover image
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = podcast.cover_image_url
    ET.SubElement(image, "title").text = podcast.podcast_title
    ET.SubElement(image, "link").text = podcast.cover_image_url

    ET.SubElement(channel, f"{{{ITUNES_NS}}}image", attrib={"href": podcast.cover_image_url})

    # Add the first episode
    _add_episode_to_channel(channel, episode)

    return _to_xml_string(rss)


def add_episode_to_existing_feed(existing_xml: str, episode: EpisodeAssets) -> str:
    """Parse an existing RSS feed, prepend a new episode, return updated XML string."""

    # Register namespace before parsing
    ET.register_namespace("itunes", ITUNES_NS)

    root = ET.fromstring(existing_xml)
    channel = root.find("channel")

    if channel is None:
        raise ValueError("Invalid RSS feed: no <channel> element found")

    # Find the first <item> to insert before it (newest episode first)
    first_item = channel.find("item")

    if first_item is not None:
        # Insert new episode before the first existing one
        index = list(channel).index(first_item)
        item = _build_episode_element(episode)
        channel.insert(index, item)
    else:
        _add_episode_to_channel(channel, episode)

    return _to_xml_string(root)


def count_episodes(xml_string: str) -> int:
    """Count the number of <item> elements in an RSS feed."""
    root = ET.fromstring(xml_string)
    channel = root.find("channel")
    if channel is None:
        return 0
    return len(channel.findall("item"))


def _add_episode_to_channel(channel: ET.Element, episode: EpisodeAssets):
    """Append an episode <item> to the channel."""
    item = _build_episode_element(episode)
    channel.append(item)


def _build_episode_element(episode: EpisodeAssets) -> ET.Element:
    """Build a single <item> element for an episode."""
    item = ET.Element("item")

    ET.SubElement(item, "title").text = episode.title
    ET.SubElement(item, "description").text = episode.description
    ET.SubElement(item, "guid", attrib={"isPermaLink": "false"}).text = episode.script_id

    pub_date = datetime.now(timezone.utc)
    ET.SubElement(item, "pubDate").text = format_datetime(pub_date)

    # Audio enclosure (required for podcast apps)
    enclosure_attribs = {
        "url": episode.audio_url,
        "type": "audio/mpeg",
    }
    if episode.duration_seconds:
        enclosure_attribs["length"] = str(episode.duration_seconds * 128000 // 8)  # approx file size
    ET.SubElement(item, "enclosure", attrib=enclosure_attribs)

    # iTunes episode metadata
    if episode.duration_seconds:
        hours = episode.duration_seconds // 3600
        minutes = (episode.duration_seconds % 3600) // 60
        seconds = episode.duration_seconds % 60
        ET.SubElement(item, f"{{{ITUNES_NS}}}duration").text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    ET.SubElement(item, f"{{{ITUNES_NS}}}summary").text = episode.description
    ET.SubElement(item, f"{{{ITUNES_NS}}}image", attrib={"href": episode.cover_image_url})
    ET.SubElement(item, f"{{{ITUNES_NS}}}explicit").text = "false"

    if episode.tags:
        ET.SubElement(item, f"{{{ITUNES_NS}}}keywords").text = ", ".join(episode.tags)

    return item


def _to_xml_string(root: ET.Element) -> str:
    """Convert ElementTree to a formatted XML string."""
    ET.indent(root, space="  ")
    xml_bytes = ET.tostring(root, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes
