from enum import Enum
from typing import Optional, Union, List
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


# Data class for VirtualPlaylist (used in grouped feed)
@dataclass
class VirtualPlaylist:
    id: int
    uuid: str
    name: str
    dreams: List["Dream"]
    created_at: str
    user: Optional["User"] = None
    displayedOwner: Optional["User"] = None


# Data class for GroupedFeedResponse
@dataclass
class GroupedFeedResponse:
    feedItems: List[FeedItem]
    virtualPlaylists: List[VirtualPlaylist]
    count: int
