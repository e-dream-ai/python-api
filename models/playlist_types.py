from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
from models.dream_types import Dream
from models.user_types import User


# Enum for DreamStatusType
class PlaylistItemType(Enum):
    PLAYLIST = "playlist"
    DREAM = "dream"
    NONE = "none"


# Data class for PlaylistItem
@dataclass
class PlaylistItem:
    id: int
    type: str
    order: int
    playlist: Optional["Playlist"] = None
    dreamItem: Optional[Dream] = None
    playlistItem: Optional["Playlist"] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


# Data class for Playlist
@dataclass
class Playlist:
    id: int
    uuid: str
    name: str
    thumbnail: str
    updated_at: str
    user: Optional[User] = None
    displayedOwner: Optional[User] = None
    items: Optional[List[PlaylistItem]] = None
    itemCount: Optional[int] = 0
    featureRank: Optional[int] = 0
    nsfw: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Data class for Playlist
@dataclass
class PlaylistResponseWrapper:
    playlist: Optional[Playlist]


# Data class for UpdatePlaylistRequest
@dataclass
class UpdatePlaylistRequest:
    name: Optional[str] = None
    featureRank: Optional[int] = None
    displayedOwner: Optional[int] = None
    nsfw: Optional[bool] = None
