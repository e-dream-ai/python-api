from enum import Enum
from typing import List, Optional, Dict, ByteString
from dataclasses import dataclass
from .user_types import User
from .vote_types import Vote


# Enum for DreamStatusType
class DreamStatusType(Enum):
    NONE = "none"
    QUEUE = "queue"
    PROCESSING = "processing"
    FAILED = "failed"
    PROCESSED = "processed"


# Enum for DreamFileType
class DreamFileType(str, Enum):
    DREAM = "dream"
    THUMBNAIL = "thumbnail"
    FILMSTRIP = "filmstrip"

    def to_dict(self):
        return self.value


# Data class for Dream
@dataclass
class Dream:
    id: int
    user: User
    uuid: str
    name: Optional[str] = None
    thumbnail: Optional[str] = None
    activityLevel: Optional[int] = 0
    original_video: Optional[str] = None
    video: Optional[str] = None
    featureRank: Optional[int] = None
    displayedOwner: Optional[User] = None
    frontendUrl: Optional[str] = None
    processedVideoSize: Optional[str] = None
    processedVideoFrames: Optional[int] = None
    processedVideoFPS: Optional[str] = None
    status: DreamStatusType = DreamStatusType.NONE
    nsfw: Optional[bool] = None
    # playlistItems: Any = None
    filmstrip: Optional[List[str]] = None
    upvotes: Optional[int] = None
    downvotes: Optional[int] = None
    processed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


# Data class for PresignedPost
@dataclass
class PresignedPost:
    url: str
    uuid: str
    fields: Dict[str, str]


# Data class for PresignedPostRequest
@dataclass
class PresignedPostRequest:
    params: Optional[PresignedPost] = None
    file: Optional[ByteString] = None


# Data class for MultipartUpload
@dataclass
class MultipartUpload:
    urls: Optional[List[str]] = None
    dream: Optional[Dream] = None
    uploadId: Optional[str] = None


# Data class for RefreshMultipartUpload
@dataclass
class RefreshMultipartUpload:
    url: Optional[str] = None
    dream: Optional[Dream] = None
    uploadId: Optional[str] = None


# Data class for MultipartUploadRequest
@dataclass
class MultipartUploadRequest:
    presignedUrl: str
    filePart: ByteString
    partNumber: int
    totalParts: int


# Data class for DreamResponseWrapper
@dataclass
class DreamResponseWrapper:
    dream: Optional[Dream]


# Data class for DreamVoteResponseWrapper
@dataclass
class DreamVoteResponseWrapper:
    vote: Optional[Vote]


# Data class for UpdateDreamRequest
@dataclass
class UpdateDreamRequest:
    name: Optional[str] = None
    video: Optional[str] = None
    thumbnail: Optional[str] = None
    activityLevel: Optional[int] = None
    featureRank: Optional[int] = None
    displayedOwner: Optional[int] = None


# Data class for SetDreamProcessedRequest
@dataclass
class SetDreamProcessedRequest:
    processedVideoSize: Optional[int] = None
    processedVideoFrames: Optional[int] = None
    processedVideoFPS: Optional[int] = None
    activityLevel: Optional[float] = None
    filmstrip: Optional[List[str]] = None
    md5: Optional[str] = None
