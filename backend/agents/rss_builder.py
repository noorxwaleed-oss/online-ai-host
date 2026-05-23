import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from backend.models.publishing import EpisodeAssets, PodcastInfo

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"

def create_new_feed(podcast: PodcastInfo, episode: EpisodeAssets) -> str:
    ET.register_namespace("itunes", ITUNES_NS)
    rss = ET.Element("rss", attrib={"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = podcast.podcast_title
    ET.SubElement(channel, "description").text = podcast.podcast_description
    ET.SubElement(channel, "language").text = podcast.language
    ET.SubElement(channel, "link").text = podcast.cover_image_url
    ET.SubElement(channel, f"{{{ITUNES_NS}}}author").text = podcast.author
    ET.SubElement(channel, f"{{{ITUNES_NS}}}summary").text = podcast.podcast_description
    ET.SubElement(channel, f"{{{ITUNES_NS}}}category", attrib={"text": podcast.category})
    ET.SubElement(channel, f"{{{ITUNES_NS}}}explicit").text = "false"
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = podcast.cover_image_url
    ET.SubElement(image, "title").text = podcast.podcast_title
    ET.SubElement(image, "link").text = podcast.cover_image_url
    ET.SubElement(channel, f"{{{ITUNES_NS}}}image", attrib={"href": podcast.cover_image_url})
    _add_episode_to_channel(channel, episode)
    return _to_xml_string(rss)

def add_episode_to_existing_feed(existing_xml: str, episode: EpisodeAssets) -> str:
    ET.register_namespace("itunes", ITUNES_NS)
    root = ET.fromstring(existing_xml)
    channel = root.find("channel")
    if channel is None: raise ValueError("Invalid RSS feed: no <channel> element found")
    first_item = channel.find("item")
    if first_item is not None:
        index = list(channel).index(first_item)
        item = _build_episode_element(episode)
        channel.insert(index, item)
    else: _add_episode_to_channel(channel, episode)
    return _to_xml_string(root)

def count_episodes(xml_string: str) -> int:
    root = ET.fromstring(xml_string)
    channel = root.find("channel")
    return len(channel.findall("item")) if channel is not None else 0

def _add_episode_to_channel(channel: ET.Element, episode: EpisodeAssets):
    item = _build_episode_element(episode)
    channel.append(item)

def _build_episode_element(episode: EpisodeAssets) -> ET.Element:
    item = ET.Element("item")
    ET.SubElement(item, "title").text = episode.title
    ET.SubElement(item, "description").text = episode.description
    ET.SubElement(item, "guid", attrib={"isPermaLink": "false"}).text = episode.script_id
    ET.SubElement(item, "pubDate").text = format_datetime(datetime.now(timezone.utc))
    enclosure_attribs = {"url": episode.audio_url, "type": "audio/mpeg"}
    if episode.duration_seconds: enclosure_attribs["length"] = str(episode.duration_seconds * 128000 // 8)
    ET.SubElement(item, "enclosure", attrib=enclosure_attribs)
    if episode.duration_seconds:
        h, m, s = episode.duration_seconds // 3600, (episode.duration_seconds % 3600) // 60, episode.duration_seconds % 60
        ET.SubElement(item, f"{{{ITUNES_NS}}}duration").text = f"{h:02d}:{m:02d}:{s:02d}"
    ET.SubElement(item, f"{{{ITUNES_NS}}}summary").text = episode.description
    ET.SubElement(item, f"{{{ITUNES_NS}}}image", attrib={"href": episode.cover_image_url})
    ET.SubElement(item, f"{{{ITUNES_NS}}}explicit").text = "false"
    return item

def _to_xml_string(root: ET.Element) -> str:
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode", xml_declaration=False)
