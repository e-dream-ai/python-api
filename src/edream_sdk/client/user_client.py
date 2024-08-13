from typing import Optional
from ..models.api_types import ApiResponse
from ..models.user_types import UserResponseWrapper
from ..utils.api_utils import deserialize_api_response


class UserClient:
    def get_logged_user(self) -> Optional[ApiResponse[UserResponseWrapper]]:
        """
        Retrieves the logged user
        Returns:
            Optional[ApiResponse[UserResponseWrapper]]: An `ApiResponse` object containing a `UserResponseWrapper`
        """
        data = self._get(f"/auth/user")
        response = deserialize_api_response(data, UserResponseWrapper)
        user = response.data.user
        return user
