from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, TypedDict
from .dream_types import Dream, DreamFileType


# Enum for FileType
class FileType(str, Enum):
    DREAM = "dream"
    THUMBNAIL = "thumbnail"
    FILMSTRIP = "filmstrip"
    KEYFRAME = "keyframe"

    def to_dict(self):
        return self.value


# Data class for CreateMultipartUploadFormValues
@dataclass
class CreateMultipartUploadFormValues(TypedDict):
    uuid: Optional[str] = None
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[int] = None
    nsfw: Optional[bool] = None
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Data class for CreateDreamFileMultipartUploadFormValues
@dataclass
class CreateDreamFileMultipartUploadFormValues(TypedDict):
    type: DreamFileType
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[int] = None
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Data class for MultipartUpload
@dataclass
class MultipartUpload(TypedDict):
    urls: List[str]
    uploadId: str
    dream: Optional[Dream]


# Data class for MultipartUploadRequest
@dataclass
class MultipartUploadRequest(TypedDict):
    presignedUrl: str
    dream: Optional[Dream]
    uploadId: str


# Data class for CompletedPart
@dataclass
class CompletedPart(TypedDict):
    ETag: str
    PartNumber: int


# Data class for RefreshMultipartUploadUrlFormValues
@dataclass
class RefreshMultipartUploadUrlFormValues(TypedDict):
    type: DreamFileType
    uploadId: str
    extension: str
    part: int
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Data class for CompleteMultipartUploadFormValues
@dataclass
class CompleteMultipartUploadFormValues(TypedDict):
    type: DreamFileType
    uploadId: str
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[List[CompletedPart]] = None
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Data class for CompleteMultipartUploadFormValues
@dataclass
class UploadFileOptions(TypedDict):
    uuid: Optional[str] = None
    processed: Optional[bool] = None
    frame_number: Optional[int] = None  # Specific to FILMSTRIP
    name: Optional[str] = None  # Specific to DREAM
    nsfw: Optional[bool] = None  # Specific to DREAM


# Data class for CompleteMultipartUploadFormValues
@dataclass
class RefreshMultipartUpload(TypedDict):
    url: str
    dream: Dream
    uploadId: str


# Data class for CompleteFileResponseWrapper
@dataclass
class CompleteFileResponseWrapper(TypedDict):
    dream: Optional[Dream]
