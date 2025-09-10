import requests
from typing import Optional, Any, Dict
from ..types.api_types import ApiResponse

EDREAM_USER_AGENT = "EdreamSDK"


class ApiClient:
    """
    A client for making HTTP requests to a backend API
    """

    def __init__(self, backend_url: str, api_key: str):
        if backend_url is None or api_key is None:
            raise ValueError(
                "backend_url and api_key must be provided for the first initialization"
            )
        self.backend_url = backend_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.api_key}",
                "User-Agent": EDREAM_USER_AGENT,
            }
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> ApiResponse:
        try:
            url = f"{self.backend_url}{endpoint}"
            filtered_data = {k: v for k, v in (data or {}).items() if v is not None}
            response = self.session.request(
                method, url, params=params, json=filtered_data
            )
            response.raise_for_status()
            return ApiResponse(response.json())

        except requests.exceptions.HTTPError as http_err:
            # Handle HTTP errors (e.g., 4xx, 5xx status codes)
            error_message = f"HTTP error occurred: {http_err}"
            error_response = (
                response.json() if response.content else "No response content"
            )
            print(error_message)
            print(f"Error details: {error_response}")
            raise

        except requests.exceptions.RequestException as req_err:
            # Handle other types of request exceptions
            print(f"Request error occurred: {req_err}")
            raise

        except ValueError as val_err:
            # Handle issues with decoding JSON
            print(f"Value error occurred: {val_err}")
            raise

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> ApiResponse:
        return ApiResponse(self._request("GET", endpoint, params=params))

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> ApiResponse:
        return self._request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> ApiResponse:
        return self._request("PUT", endpoint, data=data)

    def delete(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> ApiResponse:
        return self._request("DELETE", endpoint, data=data)


class FeedClient:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_ranked_feed(self, take: int = 10, skip: int = 0):
        params = {"take": take, "skip": skip}
        response = self.api_client.get("/feed/ranked", params=params)
        return response["data"]

    def get_feed(self, take: int = 48, skip: int = 0, search: str = None, 
                 user_uuid: str = None, feed_type: str = None, only_hidden: bool = None):
        """
        Get regular feed content
        
        Args:
            take (int): Number of items to take (default: 48)
            skip (int): Number of items to skip (default: 0)
            search (str, optional): Search query
            user_uuid (str, optional): Filter by user UUID
            feed_type (str, optional): Type filter ("dream", "playlist", "all")
            only_hidden (bool, optional): Show only hidden items
            
        Returns:
            dict: Feed response with feed items and count
        """
        params = {"take": take, "skip": skip}
        if search:
            params["search"] = search
        if user_uuid:
            params["userUUID"] = user_uuid
        if feed_type:
            params["type"] = feed_type
        if only_hidden is not None:
            params["onlyHidden"] = str(only_hidden).lower()
            
        response = self.api_client.get("/feed", params=params)
        return response["data"]

    def get_grouped_feed(self, take: int = 48, skip: int = 0, search: str = None, 
                        user_uuid: str = None, feed_type: str = None, only_hidden: bool = None):
        """
        Get grouped feed content with virtual playlists
        
        Args:
            take (int): Number of items to take (default: 48)
            skip (int): Number of items to skip (default: 0)
            search (str, optional): Search query
            user_uuid (str, optional): Filter by user UUID
            feed_type (str, optional): Type filter ("dream", "playlist", "all")
            only_hidden (bool, optional): Show only hidden items
            
        Returns:
            dict: Grouped feed response with feedItems, virtualPlaylists, and count
        """
        params = {"take": take, "skip": skip}
        if search:
            params["search"] = search
        if user_uuid:
            params["userUUID"] = user_uuid
        if feed_type:
            params["type"] = feed_type
        if only_hidden is not None:
            params["onlyHidden"] = str(only_hidden).lower()
            
        response = self.api_client.get("/feed/grouped", params=params)
        return response["data"]
