from enum import Enum
from typing import Optional, Union
from dataclasses import dataclass
from .user_types import User
from .dream_types import Dream
from .playlist_types import Playlist


# Enum for FeedItemType
class FeedItemType(Enum):
    ALL = "all"
    PLAYLIST = "playlist"
    DREAM = "dream"
    USER = "user"
    CREATOR = "creator"
    ADMIN = "admin"


# Data class for FeedItem
@dataclass
class FeedItem:
    id: int
    user: "User"
    type: FeedItemType
    dreamItem: Optional["Dream"] = None
    playlistItem: Optional["Playlist"] = None
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None
