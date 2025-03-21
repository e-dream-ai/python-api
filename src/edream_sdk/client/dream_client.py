from typing import Optional
from ..client.api_client import ApiClient
from ..types.dream_types import (
    Dream,
    Vote,
    DreamResponseWrapper,
    DreamVoteResponseWrapper,
    UpdateDreamRequest,
    SetDreamProcessedRequest,
)


class DreamClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_dream(self, uuid: str) -> Optional[Dream]:
        """
        Retrieves a dream by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Optional[Dream]: Found Dream
        """
        response = self.api_client.get(f"/dream/{uuid}")
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
            Dream: Updated dream
        """
        response = self.api_client.put(f"/dream/{uuid}", data)
        data: DreamResponseWrapper = response["data"]
        dream = data["dream"]
        return dream

    def get_dream_vote(self, uuid: str) -> Optional[Vote]:
        """
        Retrieves dream vote by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Optional[Vote]: Dream Vote data
        """
        response = self.api_client.get(f"/dream/{uuid}/vote")
        data: DreamVoteResponseWrapper = response["data"]
        vote = data["vote"]
        return vote

    def set_dream_processing(self, uuid: str) -> Dream:
        """
        Set dream to 'updating' status by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Dream: Updated dream
        """
        response = self.api_client.post(f"/dream/{uuid}/status/processing")
        data: DreamResponseWrapper = response["data"]
        dream = data["dream"]
        return dream

    def set_dream_processed(self, uuid: str, data: SetDreamProcessedRequest) -> Dream:
        """
        Set dream to 'processed' status by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Dream: Updated dream
        """
        response = self.api_client.post(f"/dream/{uuid}/status/processed", data)
        data: DreamResponseWrapper = response["data"]
        dream = data["dream"]
        return dream

    def set_dream_failed(self, uuid: str) -> Dream:
        """
        Set dream to 'failed' status by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Dream: Updated dream
        """
        response = self.api_client.post(f"/dream/{uuid}/status/failed")
        data: DreamResponseWrapper = response["data"]
        dream = data["dream"]
        return dream

    def upvote_dream(self, uuid: str) -> Dream:
        """
        Upvotes dream vote by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Dream: Voted dream
        """
        response = self.api_client.put(f"/dream/{uuid}/upvote")
        data: DreamResponseWrapper = response["data"]
        dream = data["dream"]
        return dream

    def downvote_dream(self, uuid: str) -> Dream:
        """
        Downvotes dream vote by its uuid
        Args:
            uuid (str): dream uuid
        Returns:
            Dream: Voted dream
        """
        response = self.api_client.put(f"/dream/{uuid}/downvote")
        data: DreamResponseWrapper = response["data"]
        dream = data["dream"]
        return dream

    def delete_dream(self, uuid: str) -> Optional[bool]:
        """
        Deletes a dream
        Args:
            uuid (str): dream uuid
        Returns:
            Optional[bool]: Boolean value that notifies if dream was deleted
        """
        response = self.api_client.delete(f"/dream/{uuid}")
        return response["success"]
