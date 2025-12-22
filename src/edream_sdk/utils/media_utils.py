from typing import Optional
from ..types.dream_types import DreamMediaType

ALLOWED_IMAGE_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
    "bmp",
    "webp",
    "tiff",
    "svg",
    "ico",
    "heif",
    "heic",
]

ALLOWED_VIDEO_EXTENSIONS = [
    "mp4",
    "avi",
    "mov",
    "wmv",
    "mkv",
    "flv",
    "mpeg",
    "webm",
    "ogv",
    "3gp",
    "3g2",
    "h264",
    "hevc",
    "divx",
    "xvid",
    "avchd",
]


def detect_media_type_from_extension(extension: str) -> DreamMediaType:
    """
    Detects media type from file extension
    Args:
        extension (str): File extension (with or without leading dot)
    Returns:
        DreamMediaType: IMAGE if extension is in ALLOWED_IMAGE_EXTENSIONS, VIDEO otherwise
    """
    clean_extension = extension.lower().replace(".", "")

    if clean_extension in ALLOWED_IMAGE_EXTENSIONS:
        return DreamMediaType.IMAGE

    if clean_extension in ALLOWED_VIDEO_EXTENSIONS:
        return DreamMediaType.VIDEO

    # Default to VIDEO for unknown extensions (backward compatibility)
    return DreamMediaType.VIDEO

