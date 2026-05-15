MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32



# =========================
# IMAGE SIZES
# =========================

ASPECT_RATIOS = {
    "1:1": (768, 768),
    "16:9": (1024, 576),
    "4:5": (768, 960),
    "2:3": (768, 1152)
}
