# edream_client.py
from ..client.api_client import ApiClient
from .dream_client import DreamClient
from .playlist_client import PlaylistClient
from .user_client import UserClient
from .file_client import FileClient


class EDreamClient(ApiClient, UserClient, DreamClient, PlaylistClient, FileClient):
    pass


def create_edream_client(backend_url: str, api_key: str) -> EDreamClient:
    return EDreamClient(backend_url, api_key)
