from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import Optional, List
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
class CreateMultipartUploadFormValues:
    uuid: Optional[str] = None
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[int] = None
    nsfw: Optional[bool] = None
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Data class for CreateDreamFileMultipartUploadFormValues
@dataclass
class CreateDreamFileMultipartUploadFormValues:
    type: DreamFileType
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[int] = None
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Data class for MultipartUpload
@dataclass
class MultipartUpload:
    urls: List[str]
    uploadId: str
    dream: Optional[Dream]


# Data class for MultipartUploadRequest
@dataclass
class MultipartUploadRequest:
    presignedUrl: str
    dream: Optional[Dream]
    uploadId: str


# Data class for CompletedPart
@dataclass_json
@dataclass
class CompletedPart:
    ETag: str
    PartNumber: int


# Data class for RefreshMultipartUploadUrlFormValues
@dataclass
class RefreshMultipartUploadUrlFormValues:
    type: DreamFileType
    uploadId: str
    extension: str
    part: int
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Data class for CompleteMultipartUploadFormValues
@dataclass
class CompleteMultipartUploadFormValues:
    type: DreamFileType
    uploadId: str
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[List[CompletedPart]] = None
    frameNumber: Optional[int] = None
    processed: Optional[bool] = None


# Data class for CompleteMultipartUploadFormValues
@dataclass
class UploadFileOptions:
    uuid: Optional[str] = None
    processed: Optional[bool] = None
    frame_number: Optional[int] = None  # Specific to FILMSTRIP
    name: Optional[str] = None  # Specific to DREAM
    nsfw: Optional[bool] = None  # Specific to DREAM


# Data class for CompleteMultipartUploadFormValues
@dataclass
class RefreshMultipartUpload:
    url: str
    dream: Dream
    uploadId: str


# Data class for CompleteFileResponseWrapper
@dataclass_json
@dataclass
class CompleteFileResponseWrapper:
    dream: Optional[Dream]
