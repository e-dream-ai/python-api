from enum import Enum
from typing import List, Optional, Dict, ByteString, TypedDict
from dataclasses import dataclass
from .user_types import User
from .vote_types import Vote
from .keyframe_types import Keyframe


# Enum for DreamStatusType
class DreamStatusType(Enum):
    NONE = "none"
    QUEUE = "queue"
    PROCESSING = "processing"
    FAILED = "failed"
    PROCESSED = "processed"


# Enum for DreamFileType
class DreamFileType:
    DREAM = "dream"
    THUMBNAIL = "thumbnail"
    FILMSTRIP = "filmstrip"

    def to_dict(self):
        return self.value


# Data class for Dream
@dataclass
class Dream(TypedDict):
    id: int
    uuid: str
    user: Optional[User] = None
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
    sourceUrl: Optional[str] = None
    description: Optional[str] = None
    ccbyLicense: Optional[bool] = None
    md5: Optional[str] = None
    startKeyframe: Optional[Keyframe] = None
    endKeyframe: Optional[Keyframe] = None
    processed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


# Data class for PresignedPost
@dataclass
class PresignedPost(TypedDict):
    url: str
    uuid: str
    fields: Dict[str, str]


# Data class for PresignedPostRequest
@dataclass
class PresignedPostRequest(TypedDict):
    params: Optional[PresignedPost] = None
    file: Optional[ByteString] = None


# Data class for MultipartUpload
@dataclass
class MultipartUpload(TypedDict):
    urls: Optional[List[str]] = None
    dream: Optional[Dream] = None
    uploadId: Optional[str] = None


# Data class for RefreshMultipartUpload
@dataclass
class RefreshMultipartUpload(TypedDict):
    url: Optional[str] = None
    dream: Optional[Dream] = None
    uploadId: Optional[str] = None


# Data class for MultipartUploadRequest
@dataclass
class MultipartUploadRequest(TypedDict):
    presignedUrl: str
    filePart: ByteString
    partNumber: int
    totalParts: int


# Data class for DreamResponseWrapper
@dataclass
class DreamResponseWrapper(TypedDict):
    dream: Optional[Dream]


# Data class for DreamVoteResponseWrapper
@dataclass
class DreamVoteResponseWrapper(TypedDict):
    vote: Optional[Vote]


# Data class for UpdateDreamRequest
@dataclass
class UpdateDreamRequest(TypedDict):
    name: Optional[str] = None
    video: Optional[str] = None
    thumbnail: Optional[str] = None
    activityLevel: Optional[int] = None
    featureRank: Optional[int] = None
    displayedOwner: Optional[int] = None
    startKeyframe: Optional[str] = None
    endKeyframe: Optional[str] = None


# Data class for SetDreamProcessedRequest
@dataclass
class SetDreamProcessedRequest(TypedDict):
    processedVideoSize: Optional[int] = None
    processedVideoFrames: Optional[int] = None
    processedVideoFPS: Optional[int] = None
    activityLevel: Optional[float] = None
    filmstrip: Optional[List[str]] = None
    md5: Optional[str] = None
