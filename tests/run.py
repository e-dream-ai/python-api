import json
from edream_sdk.types.playlist_types import PlaylistItemType, UpdatePlaylistRequest
from edream_sdk.types.dream_types import (
    UpdateDreamRequest,
    DreamFileType,
)
from edream_sdk.types.keyframe_types import (
    UpdateKeyframeRequest,
)
from edream_sdk.types.file_upload_types import UploadFileOptions, FileType
from edream_sdk.client import create_edream_client


def run():
    """
    Initialize ApiClient with backend_url and api_key instance
    """
    edream_client = create_edream_client(
        backend_url="http://localhost:8080/api/v1", api_key="API_KEY"
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
    # playlist = edream_client.get_playlist("14bdc320-2c06-41e4-8a90-639385c491d9")

    # print(playlist)

    # edream_client.update_playlist(
    #     "39bcfc87-d13c-4106-897f-ae490d46b0d1", {"name": "playlist updated from python"}
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
