from typing import Optional
from dataclasses import asdict
from ..client.api_client import ApiClient
from ..client.file_client import FileClient
from ..types.dream_types import Dream
from ..types.keyframe_types import Keyframe
from ..types.dream_types import DreamFileType
from ..types.playlist_types import (
    Playlist,
    PlaylistItem,
    PlaylistItemType,
    PlaylistKeyframe,
    CreatePlaylistRequest,
    UpdatePlaylistRequest,
    PlaylistResponseWrapper,
    PlaylistItemResponseWrapper,
    PlaylistKeyframeResponseWrapper,
    PlaylistItemsResponseWrapper,
    PlaylistKeyframesResponseWrapper,
)
from ..utils.file_utils import verify_file_path


class PlaylistClient:
    def __init__(self, api_client: ApiClient, file_client: FileClient):
        self.api_client = api_client
        self.file_client = file_client

    def create_playlist(self, data: CreatePlaylistRequest) -> Playlist:
        """
        Creates a new playlist
        Args:
            data (CreatePlaylistRequest): playlist creation data
        Returns:
            Playlist: Created Playlist
        """
        response = self.api_client.post("/playlist", data)
        response_data: PlaylistResponseWrapper = response["data"]
        playlist = response_data["playlist"]
        return playlist

    def get_playlist(self, uuid: str, populate_items: bool = True, populate_keyframes: bool = True) -> Playlist:
        """
        Retrieves a playlist by its uuid with optional population of items and keyframes
        Args:
            uuid (str): playlist uuid
            populate_items (bool): whether to fetch and populate items (default True for backward compatibility)
            populate_keyframes (bool): whether to fetch and populate keyframes (default True for backward compatibility)
        Returns:
            Playlist: Found Playlist with items and playlistKeyframes populated if requested
        """
        response = self.api_client.get(f"/playlist/{uuid}")
        data: PlaylistResponseWrapper = response["data"]
        playlist = data["playlist"]
        
        if populate_items:
            items_response = self.get_playlist_items(uuid, take=1, skip=0)
            total_items = items_response["totalCount"]
            
            if total_items > 0:
                all_items_response = self.get_playlist_items(uuid, take=total_items, skip=0)
                playlist["items"] = all_items_response["items"]
            else:
                playlist["items"] = []
        
        if populate_keyframes:
            keyframes_response = self.get_playlist_keyframes(uuid, take=1, skip=0)
            total_keyframes = keyframes_response["totalCount"]
            
            if total_keyframes > 0:
                all_keyframes_response = self.get_playlist_keyframes(uuid, take=total_keyframes, skip=0)
                playlist["playlistKeyframes"] = all_keyframes_response["keyframes"]
            else:
                playlist["playlistKeyframes"] = []
        
        return playlist

    def update_playlist(self, uuid: str, data: UpdatePlaylistRequest) -> Playlist:
        """
        Updates a playlist by its uuid
        Args:
            uuid (str): playlist uuid
            request_data (UpdatePlaylistRequest): playlist data
        Returns:
            Playlist: Found Playlist
        """
        response = self.api_client.put(f"/playlist/{uuid}", data)
        response_data: PlaylistResponseWrapper = response["data"]
        playlist = response_data["playlist"]
        return playlist

    def add_item_to_playlist(
        self, playlist_uuid: str, type: PlaylistItemType, item_uuid: str
    ) -> PlaylistItem:
        """
        Adds item to a playlist
        Args:
            playlist_uuid (str): playlist uuid
            type (PlaylistItemType): item type
            item_uuid (int): item uuid
        Returns:
            Playlist: Found Playlist
        """
        if type not in [PlaylistItemType.DREAM, PlaylistItemType.PLAYLIST]:
            raise Exception(f"Type not allowed, use 'dream' or 'playlist'")

        form = {"type": type.value, "uuid": item_uuid}
        response = self.api_client.put(f"/playlist/{playlist_uuid}/add-item", form)
        response_data: PlaylistItemResponseWrapper = response["data"]
        playlistItem = response_data["playlistItem"]
        return playlistItem

    def add_file_to_playlist(self, uuid: str, file_path: str) -> Optional[Dream]:
        """
        Adds a file to a playlist creating a dream
        Args:
            uuid (str): playlist uuid
            file_path (str): video file path
        Returns:
            Optional[Dream]: Created Dream
        """
        dream = self.file_client.upload_file(file_path, type=DreamFileType.DREAM)
        self.add_item_to_playlist(
            playlist_uuid=uuid, type=PlaylistItemType.DREAM, item_uuid=dream["uuid"]
        )
        return dream

    def delete_item_from_playlist(
        self,
        uuid: str,
        playlist_item_id: int,
    ) -> Optional[bool]:
        """
        Deletes item from a playlist
        Args:
            uuid (str): playlist uuid
            playlist_item_id (int): playlist item id
        Returns:
            Optional[bool]: Boolean value that notifies if item was deleted
        """
        response = self.api_client.delete(
            f"/playlist/{uuid}/remove-item/{playlist_item_id}"
        )
        return response["success"]

    def _add_keyframe_to_playlist(
        self, playlist_uuid: str, keyframe_uuid: str
    ) -> PlaylistKeyframe:
        """
        Adds keyframe to a playlist
        Args:
            playlist_uuid (str): playlist uuid
            keyframe_uuid (int): keyframe uuid
        Returns:
            Playlist: Found Playlist
        """
        form = {"uuid": keyframe_uuid}
        response = self.api_client.post(f"/playlist/{playlist_uuid}/keyframe", form)
        data: PlaylistKeyframeResponseWrapper = response["data"]
        playlistKeyframe = data["playlistKeyframe"]
        return playlistKeyframe

    def add_keyframe_to_playlist(
        self, playlist: Playlist, keyframe_name: str, file_path: Optional[str] = None
    ) -> Keyframe:
        """
        Adds Keyframe to a Playlist
        Args:
            playlist_uuid (str): playlist uuid
            keyframe_name (str): keyframe uuid
            file_path (str): file path to keyframe
        Returns:
            Keyframe: Added Keyframe
        """
        if file_path is not None:
            verify_file_path(file_path)
        keyframe: Keyframe = self._create_keyframe(
            name=keyframe_name, file_path=file_path
        )
        new_playlist_keyframe = self._add_keyframe_to_playlist(
            playlist_uuid=playlist["uuid"], keyframe_uuid=keyframe["uuid"]
        )
        playlist["playlistKeyframes"].append(new_playlist_keyframe)
        return keyframe

    def reorder_playlist(
        self,
        uuid: str,
        order: [dict],
    ) -> Optional[bool]:
        """
        Reorders the items of a playlist
        Args:
            uuid (str): playlist uuid
            order ([dict]): an array of dicts specifying new positions of current items.
                            each dict is {"id": X, "order": Y} and the ID is of the item,
                            and the order is its new position.
        Returns:
            Optional[bool]: Boolean value that notifies success
        """
        form = {"order": order}
        response = self.api_client.put(f"/playlist/{uuid}/order", form)
        return response["success"]

    def delete_keyframe_from_playlist(
        self,
        uuid: str,
        playlist_keyframe_id: int,
    ) -> Optional[bool]:
        """
        Deletes keyframe from a playlist
        Args:
            uuid (str): playlist uuid
            playlist_keyframe_id (int): playlist keyframe id
        Returns:
            Optional[bool]: Boolean value that notifies if keyframe was deleted from playlist
        """
        response = self.api_client.delete(
            f"/playlist/{uuid}/keyframe/{playlist_keyframe_id}"
        )
        return response["success"]

    def get_playlist_items(
        self, uuid: str, take: Optional[int] = None, skip: Optional[int] = None
    ) -> PlaylistItemsResponseWrapper:
        """
        Retrieves paginated playlist items
        Args:
            uuid (str): playlist uuid
            take (Optional[int]): number of items to return (default 30, max 100)
            skip (Optional[int]): number of items to skip (default 0)
        Returns:
            PlaylistItemsResponseWrapper: Paginated playlist items with total count
        """
        params = {}
        if take is not None:
            params["take"] = take
        if skip is not None:
            params["skip"] = skip
        
        response = self.api_client.get(f"/playlist/{uuid}/items", params=params)
        data: PlaylistItemsResponseWrapper = response["data"]
        return data

    def get_playlist_keyframes(
        self, uuid: str, take: Optional[int] = None, skip: Optional[int] = None
    ) -> PlaylistKeyframesResponseWrapper:
        """
        Retrieves paginated playlist keyframes
        Args:
            uuid (str): playlist uuid
            take (Optional[int]): number of keyframes to return (default 30, max 100)
            skip (Optional[int]): number of keyframes to skip (default 0)
        Returns:
            PlaylistKeyframesResponseWrapper: Paginated playlist keyframes with total count
        """
        params = {}
        if take is not None:
            params["take"] = take
        if skip is not None:
            params["skip"] = skip
        
        response = self.api_client.get(f"/playlist/{uuid}/keyframes", params=params)
        data: PlaylistKeyframesResponseWrapper = response["data"]
        return data

    def delete_playlist(self, uuid: str) -> Optional[bool]:
        """
        Deletes a playlist
        Args:
            uuid (str): playlist uuid
        Returns:
            Optional[bool]: Boolean value that notifies if keyframe was deleted
        """
        response = self.api_client.delete(f"/playlist/{uuid}")
        return response["success"]
