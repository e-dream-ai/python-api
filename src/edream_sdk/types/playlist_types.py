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


# Playlist item mapping
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


# Playlist keyframe mapping
class PlaylistKeyframe(TypedDict):
    id: int
    order: Optional[int] = None
    keyframe: Optional[Keyframe] = None
    playlist: Optional["Playlist"] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


# Playlist keyframe response mapping
class PlaylistKeyframeResponseWrapper(TypedDict):
    playlistKeyframe: Optional[PlaylistKeyframe]


# Playlist mapping
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
    totalDurationSeconds: Optional[int] = None

    @property
    def keyframes(self) -> Optional[List[Keyframe]]:
        if not self.playlistKeyframes:
            return []
        return [pk.keyframe for pk in self.playlistKeyframes]


# Playlist response mapping
class PlaylistResponseWrapper(TypedDict):
    playlist: Optional[Playlist]


# Create playlist request mapping
class CreatePlaylistRequest(TypedDict):
    name: str
    description: Optional[str] = None
    nsfw: Optional[bool] = None


# Update playlist request mapping
class UpdatePlaylistRequest(TypedDict):
    name: Optional[str] = None
    featureRank: Optional[int] = None
    displayedOwner: Optional[int] = None
    nsfw: Optional[bool] = None
    description: Optional[str] = None


# Playlist item response mapping
class PlaylistItemResponseWrapper(TypedDict):
    playlistItem: Optional[PlaylistItem]


# Data class for paginated playlist items response
class PlaylistItemsResponseWrapper(TypedDict):
    items: List[PlaylistItem]
    totalCount: int


# Data class for paginated playlist keyframes response
class PlaylistKeyframesResponseWrapper(TypedDict):
    keyframes: List[PlaylistKeyframe]
    totalCount: int
