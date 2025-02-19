from typing import Optional
from dataclasses import asdict
from ..models.api_types import ApiResponse
from ..models.keyframe_types import (
    Keyframe,
    KeyframeResponseWrapper,
    UpdateKeyframeRequest,
)
from ..models.file_upload_types import FileType, UploadFileOptions
from ..utils.api_utils import deserialize_api_response


class KeyframeClient:
    def get_keyframe(self, uuid: str) -> Optional[Keyframe]:
        """
        Retrieves a keyframe by its uuid
        Args:
            uuid (str): keyframe uuid
        Returns:
            Optional[Keyframe]: An `ApiResponse` object containing a `KeyframeResponseWrapper`
        """
        data = self._get(f"/keyframe/{uuid}")
        response = deserialize_api_response(data, KeyframeResponseWrapper)
        keyframe = response.data.keyframe
        return keyframe

    def _create_keyframe(self, name: str) -> Optional[Keyframe]:
        """
        Creates a keyframe
        Args:
            name (str): keyframe name
        Returns:
            Optional[Keyframe]: An `ApiResponse` object containing a `KeyframeResponseWrapper`
        """
        request_data_dict = {"name": name}
        data = self._post(f"/keyframe/", request_data_dict)
        response = deserialize_api_response(data, KeyframeResponseWrapper)
        keyframe = response.data.keyframe
        return keyframe

    def create_keyframe(self, name: str, file_path: str) -> Optional[Keyframe]:
        """
        Creates a keyframe
        Args:
            name (str): keyframe name
        Returns:
            Optional[Keyframe]: An `ApiResponse` object containing a `KeyframeResponseWrapper`
        """
        keyframe = self._create_keyframe(name)
        if file_path:
            self.upload_file(
                file_path=file_path,
                type=FileType.KEYFRAME,
                options=UploadFileOptions(uuid=keyframe.uuid),
            )

        return keyframe

    def update_keyframe(
        self, uuid: str, request_data: UpdateKeyframeRequest
    ) -> Keyframe:
        """
        Updates a keyframe by its uuid
        Args:
            uuid (str): keyframe uuid
            request_data (UpdateKeyframeRequest): keyframe data
        Returns:
            Keyframe: An `ApiResponse` object containing a `KeyframeResponseWrapper`
        """
        request_data_dict = asdict(request_data)
        data = self._put(f"/keyframe/{uuid}", request_data_dict)
        response = deserialize_api_response(data, KeyframeResponseWrapper)
        keyframe = response.data.keyframe
        return keyframe

    def delete_keyframe(self, uuid: str) -> Optional[ApiResponse]:
        """
        Deletes a keyframe
        Args:
            uuid (str): keyframe uuid
        Returns:
            Optional[ApiResponse]: An `ApiResponse` object
        """
        data = self._delete(f"/keyframe/{uuid}")
        response = deserialize_api_response(data, ApiResponse)
        return response.success
