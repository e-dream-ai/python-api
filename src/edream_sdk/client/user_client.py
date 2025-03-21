from typing import Optional
from ..client.api_client import ApiClient
from ..types.user_types import UserResponseWrapper, User


class UserClient:

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_logged_user(self) -> Optional[User]:
        """
        Retrieves the logged user
        Returns:
            Optional[user]: Logged `User`
        """
        response = self.api_client.get(f"/auth/user")
        data: UserResponseWrapper = response["data"]
        user = data["user"]
        return user
