import os
import time
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from edream_sdk.client import create_edream_client
from edream_sdk.types.playlist_types import CreatePlaylistRequest, PlaylistItemType, UpdatePlaylistRequest
from edream_sdk.types.dream_types import (
    UpdateDreamRequest,
    DreamFileType,
)
from edream_sdk.types.keyframe_types import (
    UpdateKeyframeRequest,
)
from edream_sdk.types.file_upload_types import UploadFileOptions, FileType

# Load environment variables from .env file
load_dotenv()

def run():
    """
    Initialize ApiClient with backend_url and api_key instance
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("ERROR: No API key found. Please check your .env file.")
        return
    
    edream_client = create_edream_client(
        backend_url="https://api-stage.infinidream.ai/api/v1",  # or "http://localhost:8080/api/v1" for local testing
        api_key=api_key
    )

    """
    User functions
    """

    # user = edream_client.get_logged_user()
    # print(user["name"])

    """
    Dream functions
    """

    # dream = edream_client.get_dream("8bdcab8b-404d-4651-b24b-42edd21f1b4d")

    # print(dream)

    # print(dream["uuid"])

    # edream_client.get_dream_vote("8bdcab8b-404d-4651-b24b-42edd21f1b4d")

    # edream_client.update_dream(
    #     "8bdcab8b-404d-4651-b24b-42edd21f1b4d", {"name": "name from python"}
    # )

    # edream_client.downvote_dream("8bdcab8b-404d-4651-b24b-42edd21f1b4d")

    # edream_client.upvote_dream("8bdcab8b-404d-4651-b24b-42edd21f1b4d")

    # edream_client.delete_dream("8bdcab8b-404d-4651-b24b-42edd21f1b4d")

    """
    Playlist functions
    """
    # playlist = edream_client.get_playlist("22e40719-0a31-408a-b8b8-3517bc4c7d8e")

    # print(playlist)

    # playlist = edream_client.create_playlist(
    #     CreatePlaylistRequest(name="Test Playlist from Python", description="This playlist was created using the Python SDK")
    # )

    # edream_client.update_playlist(
    #     "22e40719-0a31-408a-b8b8-3517bc4c7d8e", {"name": "playlist updated from python", "description": "this is a description"}
    # )

    # edream_client.add_item_to_playlist(
    #     playlist_uuid="b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4",
    #     type=PlaylistItemType.DREAM,
    #     item_uuid="d20cad5c-b294-4094-a19d-f5ab043980ae",
    # )

    # edream_client.delete_item_from_playlist(
    #     uuid="b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4", playlist_item_id=324
    # )

    # edream_client.add_file_to_playlist(
    #     uuid="b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4",
    #     file_path="path_to_file/python_video.mp4",
    # )

    # edream_client.add_keyframe_to_playlist(
    #     playlist,
    #     "keyframe from python",
    #     file_path="path_to_file/keyframe.jpg",
    # )

    # edream_client.delete_keyframe_from_playlist(
    #     uuid="14bdc320-2c06-41e4-8a90-639385c491d9", playlist_keyframe_id=16
    # )

    # result = edream_client.reorder_playlist(
    #     uuid="ab76a874-928c-45b1-88b6-b059ee54ef94", order=[{"id": 557, "order": 5}]
    # )

    # edream_client.delete_playlist("b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4")

    """
    File functions
    """
    # edream_client.upload_file(
    #     file_path="path_to_file/dream.mp4",
    #     type=DreamFileType.DREAM,
    # )

    # edream_client.download_file(
    #     "file_url",
    #     "file_path",
    # )

    """
    Upload thumbnail
    """
    # edream_client.upload_file(
    #     file_path="path_to_file/thumbnail.png",
    #     type=DreamFileType.THUMBNAIL,
    #     options={"uuid": "8bdcab8b-404d-4651-b24b-42edd21f1b4d"},
    # )

    """
    Upload filmstrip
    """
    # edream_client.upload_file(
    #     file_path="path_to_file/frame.png",
    #     type=DreamFileType.FILMSTRIP,
    #     options={"uuid": "8bdcab8b-404d-4651-b24b-42edd21f1b4d", "frame_number": 701},
    # )

    """
    Keyframe functions
    """

    # keyframe = edream_client.get_keyframe("7c38cb05-838b-4a7d-94dc-7b713270731e")

    # edream_client.update_keyframe(
    #     "7c38cb05-838b-4a7d-94dc-7b713270731e",
    #     {"name": "python updated kf"},
    # )

    # edream_client.delete_keyframe(
    #     "7c38cb05-838b-4a7d-94dc-7b713270731e",
    # )

    pass


if __name__ == "__main__":
    run()
    