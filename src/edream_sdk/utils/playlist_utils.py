from typing import List, Optional
from ..types.playlist_types import Playlist


def format_playlist(
    playlist: Playlist,
) -> Playlist:
    """
    Formats a playlist by adding keyframes or other properties.

    Args:
        playlist (Playlist): The original playlist.
    Returns:
        Playlist: A new playlist with keyframes added.
    """
    # Create a copy of the playlist to avoid modifying the original
    formatted_playlist = playlist.copy()

    # If keyframes are provided, add them to the playlist
    if playlist["playlistKeyframes"]:
        formatted_playlist["keyframes"] = [
            pk["keyframe"] for pk in playlist["playlistKeyframes"]
        ]
    else:
        # Ensure playlistKeyframes exists even if no keyframes are provided
        formatted_playlist["keyframes"] = []

    return formatted_playlist
