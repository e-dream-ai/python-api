from typing import Optional
from dataclasses import asdict
from ..models.api_types import ApiResponse
from ..models.dream_types import Dream
from ..models.dream_types import DreamFileType
from ..models.playlist_types import (
    Playlist,
    PlaylistResponseWrapper,
    PlaylistItemType,
    UpdatePlaylistRequest,
)
from ..utils.api_utils import deserialize_api_response


class PlaylistClient:
    def get_playlist(self, uuid: str) -> Playlist:
        """
        Retrieves a playlist by its uuid
        Args:
            uuid (str): playlist uuid
        Returns:
            Playlist: An `ApiResponse` object containing a `PlaylistResponseWrapper`
        """
        data = self._get(f"/playlist/{uuid}")
        response = deserialize_api_response(data, PlaylistResponseWrapper)
        playlist = response.data.playlist
        return playlist

    def update_playlist(
        self, uuid: str, request_data: UpdatePlaylistRequest
    ) -> Playlist:
        """
        Updates a playlist by its uuid
        Args:
            uuid (str): playlist uuid
            request_data (UpdatePlaylistRequest): playlist data
        Returns:
            Playlist: An `ApiResponse` object containing a `PlaylistResponseWrapper`
        """
        request_data_dict = asdict(request_data)
        data = self._put(f"/playlist/{uuid}", request_data_dict)
        response = deserialize_api_response(data, PlaylistResponseWrapper)
        playlist = response.data.playlist
        return playlist

    def add_item_to_playlist(
        self, playlist_uuid: str, type: PlaylistItemType, item_uuid: str
    ) -> Playlist:
        """
        Adds item to a playlist
        Args:
            playlist_uuid (str): playlist uuid
            type (PlaylistItemType): item type
            item_uuid (int): item uuid
        Returns:
            Playlist: An `ApiResponse` object containing a `PlaylistResponseWrapper`
        """
        form = {"type": type.value, "uuid": item_uuid}
        data = self._put(f"/playlist/{playlist_uuid}/add-item", form)
        response = deserialize_api_response(data, PlaylistResponseWrapper)
        playlist = response.data.playlist
        return playlist

    def add_file_to_playlist(self, uuid: str, file_path: str) -> Optional[Dream]:
        """
        Adds a file to a playlist creating a dream
        Args:
            uuid (str): playlist uuid
            file_path (str): video file path
        Returns:
            Optional[Dream]: Created Dream
        """
        dream = self.upload_file(file_path, type=DreamFileType.DREAM)
        self.add_item_to_playlist(
            playlist_uuid=uuid, type=PlaylistItemType.DREAM, item_uuid=dream.uuid
        )
        return dream

    def delete_item_from_playlist(
        self,
        uuid: str,
        playlist_item_id: int,
    ) -> Optional[ApiResponse]:
        """
        Deletes item from a playlist
        Args:
            uuid (str): playlist uuid
            playlist_item_id (int): playlist item id
        Returns:
            Optional[ApiResponse]: An `ApiResponse` object
        """
        data = self._delete(f"/playlist/{uuid}/remove-item/{playlist_item_id}")
        response = deserialize_api_response(data, ApiResponse)
        return response.success

    def delete_playlist(self, uuid: str) -> Optional[ApiResponse]:
        """
        Deletes a playlist
        Args:
            uuid (str): playlist uuid
        Returns:
            Optional[ApiResponse]: An `ApiResponse` object
        """
        data = self._delete(f"/playlist/{uuid}")
        response = deserialize_api_response(data, ApiResponse)
        return response.success
