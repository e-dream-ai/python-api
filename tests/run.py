from edream_sdk.models.playlist_types import PlaylistItemType, UpdatePlaylistRequest
from edream_sdk.models.dream_types import UpdateDreamRequest
from edream_sdk.client import create_edream_client


def run():
    # Initialize ApiClient with backend_url and api_key instance
    edream_client = create_edream_client(
        backend_url="http://localhost:8081/api/v1", api_key="your_api_key"
    )

    # user
    # user = edream_client.get_logged_user()

    # dream
    # dream = edream_client.get_dream("55353076-f985-4a0c-bd1b-91ee727794fb")
    # edream_client.get_dream_vote("55353076-f985-4a0c-bd1b-91ee727794fb")
    # edream_client.update_dream(
    #     "55353076-f985-4a0c-bd1b-91ee727794fb",
    #     request_data=UpdateDreamRequest(name="name python"),
    # )
    # edream_client.upvote_dream("55353076-f985-4a0c-bd1b-91ee727794fb")
    # edream_client.downvote_dream("55353076-f985-4a0c-bd1b-91ee727794fb")
    # edream_client.delete_dream("55353076-f985-4a0c-bd1b-91ee727794fb")

    # playlist
    # playlist = edream_client.get_playlist("b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4")
    # edream_client.update_playlist(
    #     "b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4",
    #     request_data=UpdatePlaylistRequest(name="name python"),
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
    # edream_client.delete_playlist("b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4")

    # file
    # edream_client.upload_file("path_to_file/python_video.mp4")
    pass


if __name__ == "__main__":
    run()
