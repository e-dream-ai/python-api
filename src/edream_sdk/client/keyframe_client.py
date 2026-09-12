from typing import Any, Dict, Optional
from ..client.api_client import ApiClient
from ..client.file_client import FileClient
from ..types.api_types import ApiResponse
from ..types.keyframe_types import (
    Keyframe,
    KeyframeResponseWrapper,
    KeyframesResponseWrapper,
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

    def get_keyframes(
        self,
        search: Optional[str] = None,
        user_uuid: Optional[str] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> KeyframesResponseWrapper:
        """
        Retrieves a page of keyframes, optionally filtered.
        Args:
            search (Optional[str]): case-insensitive substring match on name
            user_uuid (Optional[str]): restrict to one owner
            take (Optional[int]): page size (backend caps this at 500)
            skip (Optional[int]): number of keyframes to skip
        Returns:
            KeyframesResponseWrapper: keyframes plus the total match count
        """
        params: Dict[str, Any] = {}
        if search is not None:
            params["search"] = search
        if user_uuid is not None:
            params["userUUID"] = user_uuid
        if take is not None:
            params["take"] = take
        if skip is not None:
            params["skip"] = skip

        response = self.api_client.get("/keyframe", params=params)
        data: KeyframesResponseWrapper = response["data"]
        return data

    def find_keyframe_by_name(
        self, name: str, user_uuid: Optional[str] = None
    ) -> Optional[Keyframe]:
        """
        Finds a keyframe by its exact name.

        The backend's search is a substring match, so this pages through the
        matches and returns the first whose name is exactly `name`. Names are
        not unique; when several match, the most recently updated one wins,
        which is the order the backend returns.

        Args:
            name (str): exact keyframe name
            user_uuid (Optional[str]): restrict to one owner
        Returns:
            Optional[Keyframe]: the matching keyframe, or None
        """
        take = 100
        skip = 0
        while True:
            page = self.get_keyframes(
                search=name, user_uuid=user_uuid, take=take, skip=skip
            )
            keyframes = page["keyframes"]
            if not keyframes:
                return None
            for keyframe in keyframes:
                if keyframe.get("name") == name:
                    return keyframe
            skip += len(keyframes)
            if skip >= page.get("count", 0):
                return None

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
