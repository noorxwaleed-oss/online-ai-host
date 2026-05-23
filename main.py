import json

from cover_agent import CoverArtAgent


with open("", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# =========================
# GENERATE IMAGE
# =========================

agent = CoverArtAgent()

image = agent.generate(
    metadata=metadata,
    style="Colorful",
    aspect_ratio="2:3"
)

image.show()
