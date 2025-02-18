from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .user_types import User


# Data class for Keyframe
@dataclass_json
@dataclass
class Keyframe:
    uuid: str
    id: Optional[int] = None
    user: Optional[User] = None
    name: Optional[str] = None
    image: Optional[str] = None
    displayedOwner: Optional[User] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Data class for KeyframeResponseWrapper
@dataclass_json
@dataclass
class KeyframeResponseWrapper:
    keyframe: Optional[Keyframe]


# Data class for UpdateKeyframeRequest
@dataclass_json
@dataclass
class UpdateKeyframeRequest:
    name: Optional[str] = None
    displayedOwner: Optional[int] = None
