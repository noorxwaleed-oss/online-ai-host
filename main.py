import json

from cover_agent import CoverArtAgent


# =========================
# LOAD JSON
# =========================

with open("output.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)


# =========================
# GENERATE IMAGE
# =========================

agent = CoverArtAgent()

image = agent.generate(
    metadata=metadata,
    style="Minimalist",
    aspect_ratio="2:3"
)

# Save image
image.save("podcast_cover.png")

print("✅ Cover saved as podcast_cover.png")