from typing import List, Optional, TypedDict
from dataclasses import dataclass
from .user_types import User


# Keyframe mapping
class Keyframe(TypedDict):
    uuid: str
    id: Optional[int] = None
    user: Optional[User] = None
    name: Optional[str] = None
    image: Optional[str] = None
    displayedOwner: Optional[User] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Keyframe response mapping
class KeyframeResponseWrapper(TypedDict):
    keyframe: Optional[Keyframe]


# Keyframe list response mapping
class KeyframesResponseWrapper(TypedDict):
    keyframes: List[Keyframe]
    count: int


# Update keyframe request mapping
class UpdateKeyframeRequest(TypedDict):
    name: Optional[str] = None
    displayedOwner: Optional[int] = None
