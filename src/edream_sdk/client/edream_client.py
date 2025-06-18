# edream_client.py
from ..client.api_client import ApiClient
from .dream_client import DreamClient
from .keyframe_client import KeyframeClient
from .playlist_client import PlaylistClient
from .user_client import UserClient
from .file_client import FileClient
from .api_client import FeedClient


class EDreamClient(
    ApiClient, UserClient, DreamClient, KeyframeClient, PlaylistClient, FileClient
):
    def __init__(self, backend_url: str, api_key: str):
        # Initialize clients with composition (so methods can be visible between clients)
        self.api_client = ApiClient(backend_url, api_key)
        self.file_client = FileClient(self.api_client)
        self.user_client = UserClient(self.api_client)
        self.dream_client = DreamClient(self.api_client)
        self.keyframe_client = KeyframeClient(self.api_client, self.file_client)
        self.playlist_client = PlaylistClient(self.api_client, self.file_client)
        self.feed = FeedClient(self.api_client)

        # Manually set up inheritance (so methods can be use on the main client)
        ApiClient.__init__(self, backend_url, api_key)
        FileClient.__init__(self, self.api_client)
        UserClient.__init__(self, self.api_client)
        DreamClient.__init__(self, self.api_client)
        KeyframeClient.__init__(self, self.api_client, self.file_client)
        PlaylistClient.__init__(self, self.api_client, self.file_client)


def create_edream_client(backend_url: str, api_key: str) -> EDreamClient:
    return EDreamClient(backend_url, api_key)
