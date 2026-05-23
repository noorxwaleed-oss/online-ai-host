from huggingface_hub import InferenceClient
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
from config import MODEL, ASPECT_RATIOS ,HF_token_coverArt
import textwrap
from dotenv import load_dotenv
load_dotenv()


from prompts import (
    IMAGE_SYSTEM_PROMPT,
    STYLE_TEMPLATES,
    NEGATIVE_PROMPT
)


from translator import translate_text


class CoverArtAgent:

    def __init__(self):

        self.client = InferenceClient(
            provider="fal-ai",
            api_key=os.environ["HF_TOKEN_coverArt"],
        )
        self.model = MODEL
        

    # =========================
    # EXTRACT DATA
    # =========================

    def extract_data(self, metadata):

        first_topic = metadata["topics"][0]

        title = first_topic.get(
            "title",
            "Podcast"
        )

        insight = first_topic.get(
            "insight",
            "Interesting discussion"
        )

        title = translate_text(title)
        insight = translate_text(insight)

        return title, insight

    # =========================
    # BUILD PROMPT
    # =========================

    def build_prompt(self, title, insight, style):
        style_prompt = STYLE_TEMPLATES[style]
        
        short_insight = (
            insight[:150]
            if len(insight) > 150
            else insight
        )
    
        prompt = IMAGE_SYSTEM_PROMPT.format(
                style_prompt=style_prompt,
                title=title,
                short_insight=short_insight
            )

        return prompt

    # =========================
    # GENERATE IMAGE
    # =========================

    def generate(self, metadata, style="Minimalist", aspect_ratio="1:1"):
        title, insight = self.extract_data(metadata)

        prompt = self.build_prompt(
            title,
            insight,
            style
            
        )

        width, height = ASPECT_RATIOS[aspect_ratio]
        size_string = f"{width}x{height}"

      

        # Generate image
        image = self.client.text_to_image(
            prompt=prompt,
            negative_prompt=NEGATIVE_PROMPT,
            model=self.model
        )
        image = image.resize((width, height))
        # Add title
        self.add_title(
            image,
            title,
            width,
            height
        )

        return image

    # =========================
    # ADD TITLE
    # =========================

    def add_title(self, image, title, width, height):
        draw = ImageDraw.Draw(image)

        # Clean up any potential accidental newlines in the title string
        title = title.replace("\n", " ").strip()
        max_chars = 20
        wrapped_title = "\n".join(textwrap.wrap(title, width=max_chars))

        font_size = int(width * 0.06)

    # Safe cross-platform font loading block
        font = None
        font_choices = [
            "arialbd.ttf", 
            "arial.ttf", 
            "LiberationSans-Bold.ttf", 
            "DejaVuSans-Bold.ttf",
            "Arial.ttf"
        ]
        
        for font_name in font_choices:
            try:
                font = ImageFont.truetype(font_name, size=font_size)
                break
            except IOError:
                continue

        # If absolutely no system fonts are found, use the standard default font
        if font is None:
            font = ImageFont.load_default()

        # Calculate text boundaries safely
        try:
            bbox = draw.multiline_textbbox((0, 0), wrapped_title, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            # Fallback for older Pillow versions
            text_width = draw.textlength(title, font=font) if hasattr(draw, 'textlength') else width * 0.6

    # Center text
        x = (width - text_width) / 2
        y = height * 0.75

        draw.multiline_text(
            (x, y),
            wrapped_title,
            fill="white",
            font=font,
            align="center",
            stroke_width=4,
            stroke_fill="black"
        )
