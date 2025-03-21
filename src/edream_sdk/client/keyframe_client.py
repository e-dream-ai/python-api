from typing import Optional
from ..client.api_client import ApiClient
from ..client.file_client import FileClient
from ..types.api_types import ApiResponse
from ..types.keyframe_types import (
    Keyframe,
    KeyframeResponseWrapper,
    UpdateKeyframeRequest,
)
from ..types.file_upload_types import FileType, UploadFileOptions


class KeyframeClient:
    def __init__(self, api_client: ApiClient, file_client: FileClient):
        self.api_client = api_client
        self.file_client = file_client

    def get_keyframe(self, uuid: str) -> Optional[Keyframe]:
        """
        Retrieves a keyframe by its uuid
        Args:
            uuid (str): keyframe uuid
        Returns:
            Optional[Keyframe]: Found Keyframe
        """
        response = self.api_client.get(f"/keyframe/{uuid}")
        data: KeyframeResponseWrapper = response["data"]
        keyframe = data["keyframe"]
        return keyframe

    def _create_keyframe_request(self, name: str) -> Optional[Keyframe]:
        """
        Creates a keyframe
        Args:
            name (str): keyframe name
        Returns:
            Optional[Keyframe]: Found Keyframe
        """
        request_data_dict = {"name": name}
        response = self.api_client.post(f"/keyframe/", request_data_dict)
        data: KeyframeResponseWrapper = response["data"]
        keyframe = data["keyframe"]
        return keyframe

    def _create_keyframe(
        self, name: str, file_path: Optional[str] = None
    ) -> Optional[Keyframe]:
        """
        Creates a keyframe
        Args:
            name (str): keyframe name
        Returns:
            Optional[Keyframe]: Found Keyframe
        """
        keyframe = self._create_keyframe_request(name)
        if file_path:
            self.file_client.upload_file(
                file_path=file_path,
                type=FileType.KEYFRAME,
                options={"uuid": keyframe["uuid"]},
            )

        return keyframe

    def update_keyframe(self, uuid: str, data: UpdateKeyframeRequest) -> Keyframe:
        """
        Updates a keyframe by its uuid
        Args:
            uuid (str): keyframe uuid
            request_data (UpdateKeyframeRequest): keyframe data
        Returns:
            Keyframe: Found Keyframe
        """
        response = self.api_client.put(f"/keyframe/{uuid}", data)
        response_data: KeyframeResponseWrapper = response["data"]
        keyframe = response_data["keyframe"]
        return keyframe

    def delete_keyframe(self, uuid: str) -> Optional[ApiResponse]:
        """
        Deletes a keyframe
        Args:
            uuid (str): keyframe uuid
        Returns:
            Optional[bool]: Boolean value that notifies if keyframe was deleted
        """
        response = self.api_client.delete(f"/keyframe/{uuid}")
        return response["success"]
