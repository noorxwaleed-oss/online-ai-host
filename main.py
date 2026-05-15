import json

from cover_agent import CoverArtAgent




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
