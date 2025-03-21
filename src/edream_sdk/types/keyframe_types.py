from typing import Optional, TypedDict
from dataclasses import dataclass
from .user_types import User


# Data class for Keyframe
@dataclass
class Keyframe(TypedDict):
    uuid: str
    id: Optional[int] = None
    user: Optional[User] = None
    name: Optional[str] = None
    image: Optional[str] = None
    displayedOwner: Optional[User] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Data class for KeyframeResponseWrapper
@dataclass
class KeyframeResponseWrapper(TypedDict):
    keyframe: Optional[Keyframe]


# Data class for UpdateKeyframeRequest
@dataclass
class UpdateKeyframeRequest(TypedDict):
    name: Optional[str] = None
    displayedOwner: Optional[int] = None
