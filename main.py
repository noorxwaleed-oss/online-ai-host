import json

from cover_agent import CoverArtAgent




# =========================
# GENERATE IMAGE
# =========================

agent = CoverArtAgent()

image = agent.invoke(
    analyzer_output=metadata,
    style="Minimalist",
    aspect_ratio="2:3"
)

image
