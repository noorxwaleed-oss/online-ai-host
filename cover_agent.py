import torch
from PIL import ImageDraw, ImageFont
from diffusers import StableDiffusionXLPipeline

from config import (
    MODEL_ID,
    DEVICE,
    DTYPE,
    ASPECT_RATIOS
    
)

from prompts import (
    STYLE_TEMPLATES,
    NEGATIVE_PROMPT
)

from translator import translate_text


class CoverArtAgent:

    def __init__(self):

        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=DTYPE,
            use_safetensors=True
        ).to(DEVICE)

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

    def build_prompt(
        self,
        title,
        insight,
        style
    ):

        style_prompt = STYLE_TEMPLATES[style]

        short_insight = (
            insight[:150]
            if len(insight) > 150
            else insight
        )

        prompt = (
            f"{style_prompt}, "
            f"podcast cover art about {title}, "
            f"visualizing {short_insight}, "
            f"modern clean composition, "
            f"professional graphic design, centered subject"
        )

        return prompt

    # =========================
    # GENERATE IMAGE
    # =========================

    def generate(
        self,
        metadata,
        style="Minimalist",
        aspect_ratio="1:1"
    ):

        title, insight = self.extract_data(metadata)

        prompt = self.build_prompt(
            title,
            insight,
            style
        )

        width, height = ASPECT_RATIOS[
            aspect_ratio
        ]

        print("\n🎨 Generating cover...")
        print(f"Prompt: {prompt}")
        print(f"Resolution: {width}x{height}")

        image = self.pipe(
            prompt=prompt,
            height=height,
            width=width,
            num_inference_steps=25,
            guidance_scale=7,
            negative_prompt=NEGATIVE_PROMPT
        ).images[0]

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

    def add_title(
        self,
        image,
        title,
        width,
        height
    ):

        draw = ImageDraw.Draw(image)

        try:

            font_size = int(width * 0.14)

            font = ImageFont.truetype(
                "arial.ttf",
                size=font_size
            )

        except:

            font = ImageFont.load_default()

        x = int(width * 0.08)
        y = int(height * 0.82)

        draw.text(
            (x, y),
            title,
            fill="white",
            font=font,
            stroke_width=4,
            stroke_fill="black"
        )


   def invoke(self, analyzer_output, style="Minimalist", aspect_ratio="1:1"):
        
        # استدعاء دالة التوليد مباشرة باستخدام البيانات المستلمة
        return self.generate(
            metadata=analyzer_output, 
            style=style, 
            aspect_ratio=aspect_ratio
        )
