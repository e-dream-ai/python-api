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
    DreamMediaType,
    CreateDreamFromPromptRequest,
)
from edream_sdk.utils.media_utils import detect_media_type_from_extension
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
    
    backend_url = os.getenv("BACKEND_URL", "https://api-stage.infinidream.ai/api/v1")
    
    edream_client = create_edream_client(
        backend_url=backend_url,
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

    # Transfer dream ownership to a different user (requires admin privileges)
    # dream_uuid = "58ab0c35-3391-4896-ae3f-6c753e13ba74"
    # new_owner_uuid = "426ae4da-4bab-433d-ba72-a1806000aa86"
    
    # # Update the dream's owner using the user's UUID
    # updated_dream = edream_client.update_dream(
    #     dream_uuid,
    #     {"user": new_owner_uuid}
    # )
    # print(f"Updated dream {dream_uuid}")
    # print(f"New owner: {updated_dream.get('user', {}).get('name', 'N/A')}")
    # print(f"New owner UUID: {updated_dream.get('user', {}).get('uuid', 'N/A')}")

    # edream_client.downvote_dream("8bdcab8b-404d-4651-b24b-42edd21f1b4d")

    # edream_client.upvote_dream("8bdcab8b-404d-4651-b24b-42edd21f1b4d")

    # edream_client.delete_dream("8bdcab8b-404d-4651-b24b-42edd21f1b4d")

    """
    MediaType functions - Image Dreams
    """

    # Test 1: Upload image file with explicit mediaType (correct way to create image dream without prompt)
    # image_dream = edream_client.upload_file(
    #     file_path="path_to_file/image.jpg",
    #     type=FileType.DREAM,
    #     options={
    #         "name": "My Image Dream",
    #         "mediaType": DreamMediaType.IMAGE
    #     }
    # )
    # print(f"Uploaded image dream: {image_dream['uuid']}")
    # print(f"Media type: {image_dream['mediaType']}")  # Should be DreamMediaType.IMAGE

    # Test 2: Upload image file without mediaType (backend will auto-detect)
    # image_dream = edream_client.upload_file(
    #     file_path="path_to_file/image.png",
    #     type=FileType.DREAM,
    #     options={"name": "Auto-detected Image Dream"}
    # )
    # print(f"Uploaded image dream (auto-detected): {image_dream['uuid']}")
    # print(f"Media type: {image_dream['mediaType']}")  # Should be DreamMediaType.IMAGE (auto-detected)

    """
    Playlist functions
    """
    # playlist = edream_client.get_playlist("bd5615c2-5a68-4e33-b9c1-6649fb09dc03")
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

    # playlist_items = edream_client.get_playlist_items("13489b20-cc0b-4923-8ea8-3f64015fe389")
    # print(f"Playlist items: {playlist_items['items']}")
    # print(f"Total items count: {playlist_items['totalCount']}")

    # playlist_items_paginated = edream_client.get_playlist_items(
    #     "13489b20-cc0b-4923-8ea8-3f64015fe389", take=10, skip=0
    # )
    # print(f"Playlist items: {playlist_items_paginated['items']}")
    # print(f"Paginated playlist items (take=10, skip=0): {len(playlist_items_paginated['items'])} items")

    # playlist_keyframes = edream_client.get_playlist_keyframes("13489b20-cc0b-4923-8ea8-3f64015fe389")
    # print(f"Playlist keyframes: {playlist_keyframes['keyframes']}")
    # print(f"Total keyframes count: {playlist_keyframes['totalCount']}")

    # playlist_keyframes_paginated = edream_client.get_playlist_keyframes(
    #     "13489b20-cc0b-4923-8ea8-3f64015fe389", take=5, skip=0
    # )
    # print(f"Playlist keyframes: {playlist_keyframes_paginated['keyframes']}")
    # print(f"Paginated playlist keyframes (take=5, skip=0): {len(playlist_keyframes_paginated['keyframes'])} keyframes")

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

    """
    Feed functions
    """
    
    # Test get_ranked_feed
    # ranked_feed = edream_client.feed.get_ranked_feed(take=10, skip=0)
    # print(f"Ranked feed count: {ranked_feed['count']}")
    # print(f"Ranked feed items: {len(ranked_feed['feed'])}")
    
    # Test get_feed (regular feed)
    # regular_feed = edream_client.feed.get_feed(take=20, skip=0)
    # print(f"Regular feed count: {regular_feed['count']}")
    # print(f"Regular feed items: {len(regular_feed['feed'])}")
    
    # Test get_grouped_feed (NEW ENDPOINT)
    # grouped_feed = edream_client.feed.get_grouped_feed(take=48, skip=0)
    # print(f"Grouped feed count: {grouped_feed['count']}")
    # print(f"Grouped feed items: {len(grouped_feed['feedItems'])}")
    # print(f"Virtual playlists: {len(grouped_feed['virtualPlaylists'])}")
    pass


if __name__ == "__main__":
    run()
    
