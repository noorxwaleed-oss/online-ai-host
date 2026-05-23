from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont
import textwrap
from backend.config.settings import settings
from backend.agents.prompts import (
    IMAGE_SYSTEM_PROMPT,
    STYLE_TEMPLATES,
    NEGATIVE_PROMPT
)
from backend.utils.translator import translate_text

class CoverArtAgent:
    def __init__(self):
        self.client = InferenceClient(
            provider="fal-ai",
            api_key=settings.HF_TOKEN_COVERART,
        )
        self.model = settings.IMAGE_MODEL

    def extract_data(self, metadata):
        first_topic = metadata["topics"][0]
        title = first_topic.get("title", "Podcast")
        insight = first_topic.get("insight", "Interesting discussion")
        title = translate_text(title)
        insight = translate_text(insight)
        return title, insight

    def build_prompt(self, title, insight, style):
        style_prompt = STYLE_TEMPLATES[style]
        short_insight = insight[:150] if len(insight) > 150 else insight
        prompt = IMAGE_SYSTEM_PROMPT.format(
            style_prompt=style_prompt,
            title=title,
            short_insight=short_insight
        )
        return prompt

    def generate(self, metadata, style="Minimalist", aspect_ratio="1:1"):
        title, insight = self.extract_data(metadata)
        prompt = self.build_prompt(title, insight, style)
        width, height = settings.ASPECT_RATIOS[aspect_ratio]
        
        image = self.client.text_to_image(
            prompt=prompt,
            negative_prompt=NEGATIVE_PROMPT,
            model=self.model
        )
        image = image.resize((width, height))
        self.add_title(image, title, width, height)
        return image

    def add_title(self, image, title, width, height):
        draw = ImageDraw.Draw(image)
        title = title.replace("\n", " ").strip()
        max_chars = 20
        wrapped_title = "\n".join(textwrap.wrap(title, width=max_chars))
        font_size = int(width * 0.06)
        
        font = None
        font_choices = ["arialbd.ttf", "arial.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf", "Arial.ttf"]
        for font_name in font_choices:
            try:
                font = ImageFont.truetype(font_name, size=font_size)
                break
            except IOError:
                continue
        if font is None:
            font = ImageFont.load_default()

        try:
            bbox = draw.multiline_textbbox((0, 0), wrapped_title, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            text_width = draw.textlength(title, font=font) if hasattr(draw, 'textlength') else width * 0.6

        x = (width - text_width) / 2
        y = height * 0.75
        draw.multiline_text((x, y), wrapped_title, fill="white", font=font, align="center", stroke_width=4, stroke_fill="black")
