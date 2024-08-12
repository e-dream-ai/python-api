from typing import Optional
from ..client.api_client import ApiClient
from ..models.api_types import ApiResponse
from ..models.user_types import UserResponseWrapper
from ..utils.api_utils import deserialize_api_response


def get_logged_user() -> Optional[ApiResponse[UserResponseWrapper]]:
    """
    Retrieves the logged user
    Returns:
        Optional[ApiResponse[UserResponseWrapper]]: An `ApiResponse` object containing a `UserResponseWrapper`
    """
    client = ApiClient.get_instance()
    data = client.get(f"/auth/user")
    response = deserialize_api_response(data, UserResponseWrapper)
    user = response.data.user
    return user
