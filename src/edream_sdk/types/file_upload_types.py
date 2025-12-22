from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, TypedDict, Callable
from .dream_types import Dream, DreamFileType, DreamMediaType


# Enum for FileType
class FileType(str, Enum):
    DREAM = "dream"
    THUMBNAIL = "thumbnail"
    FILMSTRIP = "filmstrip"
    KEYFRAME = "keyframe"

    def to_dict(self):
        return self.value


# Create multipart upload form values mapping
class CreateMultipartUploadFormValues(TypedDict):
    uuid: Optional[str] = None
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[int] = None
    nsfw: Optional[bool] = None
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None
    mediaType: Optional[DreamMediaType] = None


# Create dream file multipart upload form values mapping
class CreateDreamFileMultipartUploadFormValues(TypedDict):
    type: DreamFileType
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[int] = None
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Multipart upload mapping
class MultipartUpload(TypedDict):
    urls: List[str]
    uploadId: str
    dream: Optional[Dream]


# Multipart upload request mapping
class MultipartUploadRequest(TypedDict):
    presignedUrl: str
    dream: Optional[Dream]
    uploadId: str


# Completed part mapping
class CompletedPart(TypedDict):
    ETag: str
    PartNumber: int


# Refresh multipart upload URL form values mapping
class RefreshMultipartUploadUrlFormValues(TypedDict):
    type: DreamFileType
    uploadId: str
    extension: str
    part: int
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Complete multipart upload form values mapping
class CompleteMultipartUploadFormValues(TypedDict):
    type: DreamFileType
    uploadId: str
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[List[CompletedPart]] = None
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


ProgressCallback = Callable[[int, int, float], None]


# Upload file options mapping
class UploadFileOptions(TypedDict):
    uuid: Optional[str] = None
    processed: Optional[bool] = None
    frame_number: Optional[int] = None  # Specific to FILMSTRIP
    name: Optional[str] = None  # Specific to DREAM
    nsfw: Optional[bool] = None  # Specific to DREAM
    mediaType: Optional[DreamMediaType] = None  # Specific to DREAM - VIDEO or IMAGE
    progress_callback: Optional[ProgressCallback] = None  # Optional progress callback
    progress_interval: Optional[float] = None  # Interval in seconds between progress updates (default 1.0)


# Refresh multipart upload mapping
class RefreshMultipartUpload(TypedDict):
    url: str
    dream: Dream
    uploadId: str


# Complete file response wrapper mapping
class CompleteFileResponseWrapper(TypedDict):
    dream: Optional[Dream]
