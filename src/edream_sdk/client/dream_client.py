from typing import Optional
from dataclasses import asdict
from ..models.api_types import ApiResponse
from ..models.dream_types import (
    Dream,
    DreamResponseWrapper,
    DreamVoteResponseWrapper,
    UpdateDreamRequest,
    SetDreamProcessedRequest,
)
from ..utils.api_utils import deserialize_api_response


class DreamClient:
    def get_dream(self, uuid: str) -> Optional[Dream]:
        """
        Retrieves a dream by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Optional[Dream]: An `ApiResponse` object containing a `DreamResponseWrapper`
        """
        response: ApiResponse = self._get(f"/dream/{uuid}")
        data: DreamResponseWrapper = response["data"]
        dream = data["dream"]
        return dream

    def update_dream(self, uuid: str, data: UpdateDreamRequest) -> Dream:
        """
        Updates a dream by its uuid
        Args:
            uuid (str): dream uuid
            request_data (UpdateDreamRequest): dream data
        Returns:
            Dream: An `ApiResponse` object containing a `DreamResponseWrapper`
        """
        response: ApiResponse = self._put(f"/dream/{uuid}", data)
        data: DreamResponseWrapper = response["data"]
        dream = data["dream"]
        return dream

    def get_dream_vote(
        self, uuid: str
    ) -> Optional[ApiResponse[DreamVoteResponseWrapper]]:
        """
        Retrieves dream vote by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Optional[ApiResponse[DreamVoteResponseWrapper]]: An `ApiResponse` object containing a `DreamVoteResponseWrapper`
        """
        data = self._get(f"/dream/{uuid}/vote")
        response = deserialize_api_response(data, DreamVoteResponseWrapper)
        vote = response.data.vote
        return vote

    def set_dream_processing(self, uuid: str) -> Dream:
        """
        Set dream to 'updating' status by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Dream: An `ApiResponse` object containing a `DreamResponseWrapper`
        """
        data = self._post(f"/dream/{uuid}/status/processing")
        response = deserialize_api_response(data, DreamResponseWrapper)
        dream = response.data.dream
        return dream

    def set_dream_processed(
        self, uuid: str, request_data: SetDreamProcessedRequest
    ) -> Dream:
        """
        Set dream to 'processed' status by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Dream: An `ApiResponse` object containing a `DreamResponseWrapper`
        """
        request_data_dict = asdict(request_data)
        data = self._post(f"/dream/{uuid}/status/processed", request_data_dict)
        response = deserialize_api_response(data, DreamResponseWrapper)
        dream = response.data.dream
        return dream

    def set_dream_failed(self, uuid: str) -> Dream:
        """
        Set dream to 'failed' status by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Dream: An `ApiResponse` object containing a `DreamResponseWrapper`
        """
        data = self._post(f"/dream/{uuid}/status/failed")
        response = deserialize_api_response(data, DreamResponseWrapper)
        dream = response.data.dream
        return dream

    def upvote_dream(self, uuid: str) -> Dream:
        """
        Upvotes dream vote by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Optional[ApiResponse[DreamVoteResponseWrapper]]: An `ApiResponse` object containing a `DreamVoteResponseWrapper`
        """
        data = self._put(f"/dream/{uuid}/upvote")
        response = deserialize_api_response(data, DreamResponseWrapper)
        dream = response.data.dream
        return dream

    def downvote_dream(self, uuid: str) -> Dream:
        """
        Downvotes dream vote by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Optional[ApiResponse[DreamVoteResponseWrapper]]: An `ApiResponse` object containing a `DreamVoteResponseWrapper`
        """
        data = self._put(f"/dream/{uuid}/downvote")
        response = deserialize_api_response(data, DreamResponseWrapper)
        dream = response.data.dream
        return dream

    def delete_dream(self, uuid: str) -> Optional[ApiResponse]:
        """
        Deletes a dream
        Args:
            uuid (str): dream uuid
        Returns:
            Optional[ApiResponse]: An `ApiResponse` object
        """
        data = self._delete(f"/dream/{uuid}")
        response = deserialize_api_response(data, ApiResponse)
        return response.success
