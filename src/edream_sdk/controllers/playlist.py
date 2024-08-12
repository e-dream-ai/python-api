from typing import Optional
from dataclasses import asdict
from ..client.api_client import ApiClient
from ..models.api_types import ApiResponse
from ..models.dream_types import Dream
from ..models.playlist_types import (
    PlaylistResponseWrapper,
    PlaylistItemType,
    UpdatePlaylistRequest,
)
from ..controllers.file_upload import upload_file
from ..utils.api_utils import deserialize_api_response


def get_playlist(uuid: str) -> Optional[ApiResponse[PlaylistResponseWrapper]]:
    """
    Retrieves a playlist by its uuid
    Args:
        uuid (str): playlist uuid
    Returns:
        Optional[ApiResponse[PlaylistResponseWrapper]]: An `ApiResponse` object containing a `PlaylistResponseWrapper`
    """
    client = ApiClient.get_instance()
    data = client.get(f"/playlist/{uuid}")
    response = deserialize_api_response(data, PlaylistResponseWrapper)
    playlist = response.data.playlist
    return playlist


def update_playlist(
    uuid: str, request_data: UpdatePlaylistRequest
) -> Optional[ApiResponse[PlaylistResponseWrapper]]:
    """
    Updates a playlist by its uuid
    Args:
        uuid (str): playlist uuid
        request_data (UpdatePlaylistRequest): playlist data
    Returns:
        Optional[ApiResponse[PlaylistResponseWrapper]]: An `ApiResponse` object containing a `PlaylistResponseWrapper`
    """
    client = ApiClient.get_instance()
    request_data_dict = asdict(request_data)
    data = client.put(f"/playlist/{uuid}", request_data_dict)
    response = deserialize_api_response(data, PlaylistResponseWrapper)
    playlist = response.data.playlist
    return playlist


def add_item_to_playlist(
    playlist_uuid: str, type: PlaylistItemType, item_uuid: str
) -> Optional[ApiResponse[PlaylistResponseWrapper]]:
    """
    Adds item to a playlist
    Args:
        playlist_uuid (str): playlist uuid
        type (PlaylistItemType): item type
        item_uuid (int): item uuid
    Returns:
        Optional[ApiResponse[PlaylistResponseWrapper]]: An `ApiResponse` object containing a `PlaylistResponseWrapper`
    """
    client = ApiClient.get_instance()
    form = {"type": type.value, "uuid": item_uuid}
    data = client.put(f"/playlist/{playlist_uuid}/add-item", form)
    response = deserialize_api_response(data, PlaylistResponseWrapper)
    playlist = response.data.playlist
    return playlist


def add_file_to_playlist(uuid: str, file_path: str) -> Optional[Dream]:
    """
    Adds a file to a playlist creating a dream
    Args:
        uuid (str): playlist uuid
        file_path (str): video file path
    Returns:
        Optional[Dream]: Created Dream
    """
    dream = upload_file(file_path)
    add_item_to_playlist(
        playlist_uuid=uuid, type=PlaylistItemType.DREAM, item_uuid=dream.uuid
    )
    return dream


def delete_item_from_playlist(
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
    client = ApiClient.get_instance()
    data = client.delete(f"/playlist/{uuid}/remove-item/{playlist_item_id}")
    response = deserialize_api_response(data, ApiResponse)
    return response.success


def delete_playlist(uuid: str) -> Optional[ApiResponse]:
    """
    Deletes a playlist
    Args:
        uuid (str): playlist uuid
    Returns:
        Optional[ApiResponse]: An `ApiResponse` object
    """
    client = ApiClient.get_instance()
    data = client.delete(f"/playlist/{uuid}")
    response = deserialize_api_response(data, ApiResponse)
    return response.success
