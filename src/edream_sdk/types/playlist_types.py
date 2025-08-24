from enum import Enum
from typing import List, Optional, TypedDict
from dataclasses import dataclass
from .user_types import User
from .dream_types import Dream
from .keyframe_types import Keyframe


# Enum for DreamStatusType
class PlaylistItemType(Enum):
    PLAYLIST = "playlist"
    DREAM = "dream"
    NONE = "none"


# Data class for PlaylistItem
@dataclass
class PlaylistItem(TypedDict):
    id: int
    type: str
    order: int
    playlist: Optional["Playlist"] = None
    dreamItem: Optional[Dream] = None
    playlistItem: Optional["Playlist"] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


# Data class for PlaylistKeyframe
@dataclass
class PlaylistKeyframe(TypedDict):
    id: int
    order: Optional[int] = None
    keyframe: Optional[Keyframe] = None
    playlist: Optional["Playlist"] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


# Data class for Playlist
@dataclass
class PlaylistKeyframeResponseWrapper(TypedDict):
    playlistKeyframe: Optional[PlaylistKeyframe]


# Data class for Playlist
@dataclass
class Playlist(TypedDict):
    id: int
    uuid: str
    name: str
    thumbnail: str
    updated_at: str
    user: Optional[User] = None
    displayedOwner: Optional[User] = None
    items: Optional[List[PlaylistItem]] = None
    playlistKeyframes: Optional[List[PlaylistKeyframe]] = None
    keyframes: Optional[List[Keyframe]] = None
    itemCount: Optional[int] = 0
    featureRank: Optional[int] = 0
    nsfw: Optional[bool] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def keyframes(self) -> Optional[List[Keyframe]]:
        if not self.playlistKeyframes:
            return []
        return [pk.keyframe for pk in self.playlistKeyframes]


# Data class for Playlist response
@dataclass
class PlaylistResponseWrapper(TypedDict):
    playlist: Optional[Playlist]


# Data class for CreatePlaylistRequest
@dataclass
class CreatePlaylistRequest(TypedDict):
    name: str
    description: Optional[str] = None
    nsfw: Optional[bool] = None
    # Note: 'hidden' field is only allowed for admin users and should not be included in regular requests


# Data class for UpdatePlaylistRequest
@dataclass
class UpdatePlaylistRequest(TypedDict):
    name: Optional[str] = None
    featureRank: Optional[int] = None
    displayedOwner: Optional[int] = None
    nsfw: Optional[bool] = None
    description: Optional[str] = None


# Data class for PlaylistItem response
@dataclass
class PlaylistItemResponseWrapper(TypedDict):
    playlistItem: Optional[PlaylistItem]
