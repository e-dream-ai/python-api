from typing import Optional
from dataclasses import asdict
from client.api_client import ApiClient
from models.api_types import ApiResponse
from models.dream_types import (
    DreamResponseWrapper,
    DreamVoteResponseWrapper,
    UpdateDreamRequest,
)
from utils.api_utils import deserialize_api_response


def get_dream(uuid: str) -> Optional[ApiResponse[DreamResponseWrapper]]:
    """
    Retrieves a dream by its uuid
    Args:
        uuid (str): dream uuid
    Returns:
        Optional[ApiResponse[DreamResponseWrapper]]: An `ApiResponse` object containing a `DreamResponseWrapper`
    """
    client = ApiClient.get_instance()
    data = client.get(f"/dream/{uuid}")
    response = deserialize_api_response(data, DreamResponseWrapper)
    dream = response.data.dream
    return dream


def update_dream(
    uuid: str, request_data: UpdateDreamRequest
) -> Optional[ApiResponse[DreamResponseWrapper]]:
    """
    Updates a dream by its uuid
    Args:
        uuid (str): dream uuid
        request_data (UpdateDreamRequest): dream data
    Returns:
        Optional[ApiResponse[DreamResponseWrapper]]: An `ApiResponse` object containing a `DreamResponseWrapper`
    """
    client = ApiClient.get_instance()
    request_data_dict = asdict(request_data)
    data = client.put(f"/dream/{uuid}", request_data_dict)
    response = deserialize_api_response(data, DreamResponseWrapper)
    dream = response.data.dream
    return dream


def get_dream_vote(uuid: str) -> Optional[ApiResponse[DreamVoteResponseWrapper]]:
    """
    Retrieves dream vote by its uuid
    Args:
        uuid (str): dream uuid
    Returns:
        Optional[ApiResponse[DreamVoteResponseWrapper]]: An `ApiResponse` object containing a `DreamVoteResponseWrapper`
    """
    client = ApiClient.get_instance()
    data = client.get(f"/dream/{uuid}/vote")
    response = deserialize_api_response(data, DreamVoteResponseWrapper)
    vote = response.data.vote
    return vote


def upvote_dream(uuid: str) -> Optional[ApiResponse[DreamResponseWrapper]]:
    """
    Upvotes dream vote by its uuid
    Args:
        uuid (str): dream uuid
    Returns:
        Optional[ApiResponse[DreamVoteResponseWrapper]]: An `ApiResponse` object containing a `DreamVoteResponseWrapper`
    """
    client = ApiClient.get_instance()
    data = client.put(f"/dream/{uuid}/upvote")
    response = deserialize_api_response(data, DreamResponseWrapper)
    dream = response.data.dream
    return dream


def downvote_dream(uuid: str) -> Optional[ApiResponse[DreamResponseWrapper]]:
    """
    Downvotes dream vote by its uuid
    Args:
        uuid (str): dream uuid
    Returns:
        Optional[ApiResponse[DreamVoteResponseWrapper]]: An `ApiResponse` object containing a `DreamVoteResponseWrapper`
    """
    client = ApiClient.get_instance()
    data = client.put(f"/dream/{uuid}/downvote")
    response = deserialize_api_response(data, DreamResponseWrapper)
    dream = response.data.dream
    return dream


def delete_dream(uuid: str) -> Optional[ApiResponse[ApiResponse]]:
    """
    Deletes a dream
    Args:
        uuid (str): dream uuid
    Returns:
        Optional[ApiResponse]: An `ApiResponse` object
    """
    client = ApiClient.get_instance()
    data = client.delete(f"/dream/{uuid}")
    response = deserialize_api_response(data, ApiResponse)
    return response.success
