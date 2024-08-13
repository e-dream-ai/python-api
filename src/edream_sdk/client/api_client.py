import requests
from typing import Optional, Any, Dict


class ApiClient:
    """
    A client for making HTTP requests to a backend API
    """

    def __init__(
        self, backend_url: Optional[str] = None, api_key: Optional[str] = None
    ):
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
            }
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            url = f"{self.backend_url}{endpoint}"
            filtered_data = {k: v for k, v in (data or {}).items() if v is not None}
            response = self.session.request(
                method, url, params=params, json=filtered_data
            )
            response.raise_for_status()
            return response.json()

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

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("POST", endpoint, data=data)

    def _put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("PUT", endpoint, data=data)

    def _delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("DELETE", endpoint, data=data)
