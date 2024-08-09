import requests
from typing import Optional, Any, Dict


class ApiClient:
    """
    A client for making HTTP requests to a backend API
    Ensures that only one instance of ApiClient can exist (singleton pattern)
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ApiClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self, backend_url: Optional[str] = None, api_key: Optional[str] = None
    ):
        # Ensure the constructor is only run once
        if not self._initialized:
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
            self.initialized = True

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError(
                "ApiClient is not initialized, call ApiClient(backend_url, api_key) first"
            )
        return cls._instance

    def request(
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

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PUT", endpoint, data=data)

    def delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("DELETE", endpoint, data=data)


# Module-level variable to hold the initialized ApiClient instance
api_client_instance = None


def initialize_api_client(backend_url: str, api_key: str):
    global api_client_instance
    if api_client_instance is None:
        api_client_instance = ApiClient(backend_url=backend_url, api_key=api_key)
    return api_client_instance
