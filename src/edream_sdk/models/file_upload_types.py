from dataclasses import dataclass
from typing import Optional, List
from .dream_types import Dream


# Data class for CreateMultipartUploadFormValues
@dataclass
class CreateMultipartUploadFormValues:
    uuid: Optional[str] = None
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[int] = None
    nsfw: Optional[bool] = None


# Data class for MultipartUpload
@dataclass
class MultipartUpload:
    urls: List[str]
    dream: Dream
    uploadId: str


# Data class for MultipartUploadRequest
@dataclass
class MultipartUploadRequest:
    presignedUrl: str
    dream: Dream
    uploadId: str


# Data class for CompletedPart
@dataclass
class CompletedPart:
    ETag: str
    PartNumber: int


# Data class for RefreshMultipartUploadUrlFormValues
@dataclass
class RefreshMultipartUploadUrlFormValues:
    extension: str
    uploadId: str
    part: int


# Data class for CompleteMultipartUploadFormValues
@dataclass
class CompleteMultipartUploadFormValues:
    name: Optional[str] = None
    extension: Optional[str] = None
    parts: Optional[List[CompletedPart]] = None
    uploadId: Optional[str] = None


# Data class for CompleteMultipartUploadFormValues
@dataclass
class RefreshMultipartUpload:
    url: str
    dream: Dream
    uploadId: str
