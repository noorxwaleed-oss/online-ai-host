import cloudinary
import cloudinary.uploader
from backend.config.settings import settings

def configure_cloudinary():
    return cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET
    )

cloudinary_config = configure_cloudinary()
