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


# Enum for DreamMediaType
class DreamMediaType(Enum):
    VIDEO = "video"
    IMAGE = "image"


# Enum for DreamFileType
class DreamFileType:
    DREAM = "dream"
    THUMBNAIL = "thumbnail"
    FILMSTRIP = "filmstrip"

    def to_dict(self):
        return self.value


# Dream mapping
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
    processedMediaWidth: Optional[int] = None
    processedMediaHeight: Optional[int] = None
    status: DreamStatusType = DreamStatusType.NONE
    mediaType: Optional[DreamMediaType] = None
    nsfw: Optional[bool] = None
    # playlistItems: Any = None
    filmstrip: Optional[List[str]] = None
    upvotes: Optional[int] = None
    downvotes: Optional[int] = None
    sourceUrl: Optional[str] = None
    description: Optional[str] = None
    ccbyLicense: Optional[bool] = None
    md5: Optional[str] = None
    prompt: Optional[Dict] = None
    startKeyframe: Optional[Keyframe] = None
    endKeyframe: Optional[Keyframe] = None
    processed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


# Presigned post mapping
class PresignedPost(TypedDict):
    url: str
    uuid: str
    fields: Dict[str, str]


# Presigned post request mapping
class PresignedPostRequest(TypedDict):
    params: Optional[PresignedPost] = None
    file: Optional[ByteString] = None


# Multipart upload mapping
class MultipartUpload(TypedDict):
    urls: Optional[List[str]] = None
    dream: Optional[Dream] = None
    uploadId: Optional[str] = None


# Refresh multipart upload mapping
class RefreshMultipartUpload(TypedDict):
    url: Optional[str] = None
    dream: Optional[Dream] = None
    uploadId: Optional[str] = None


# Multipart upload request mapping
class MultipartUploadRequest(TypedDict):
    presignedUrl: str
    filePart: ByteString
    partNumber: int
    totalParts: int


# Dream response wrapper mapping
class DreamResponseWrapper(TypedDict):
    dream: Optional[Dream]


# Dream vote response wrapper mapping
class DreamVoteResponseWrapper(TypedDict):
    vote: Optional[Vote]


# Update dream request mapping
class UpdateDreamRequest(TypedDict):
    name: Optional[str] = None
    video: Optional[str] = None
    thumbnail: Optional[str] = None
    activityLevel: Optional[int] = None
    featureRank: Optional[int] = None
    displayedOwner: Optional[int] = None
    startKeyframe: Optional[str] = None
    endKeyframe: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[Dict] = None
    mediaType: Optional[DreamMediaType] = None


# Create dream from prompt request mapping
class CreateDreamFromPromptRequest(TypedDict):
    name: str
    prompt: Optional[Dict] = None
    description: Optional[str] = None
    sourceUrl: Optional[str] = None
    nsfw: Optional[bool] = None
    hidden: Optional[bool] = None
    ccbyLicense: Optional[bool] = None
    mediaType: Optional[DreamMediaType] = None


# Set dream processed request mapping
class SetDreamProcessedRequest(TypedDict):
    processedVideoSize: Optional[int] = None
    processedVideoFrames: Optional[int] = None
    processedVideoFPS: Optional[int] = None
    processedMediaWidth: Optional[int] = None
    processedMediaHeight: Optional[int] = None
    activityLevel: Optional[float] = None
    filmstrip: Optional[List[str]] = None
    md5: Optional[str] = None
