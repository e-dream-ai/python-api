from client.api_client import initialize_api_client
from controllers.user import get_logged_user
from controllers.dream import (
    get_dream,
    update_dream,
    get_dream_vote,
    upvote_dream,
    downvote_dream,
    delete_dream,
)
from controllers.playlist import (
    get_playlist,
    update_playlist,
    add_item_to_playlist,
    add_file_to_playlist,
    delete_item_from_playlist,
    delete_playlist,
)
from controllers.file_upload import upload_file
from models.playlist_types import PlaylistItemType, UpdatePlaylistRequest
from models.dream_types import UpdateDreamRequest


def run():
    # Initialize ApiClient with backend_url and api_key instance
    initialize_api_client(
        backend_url="http://localhost:8081/api/v1", api_key="your_api_key"
    )

    # user
    # user = get_logged_user()
    # print(user)

    # dream
    # get_dream("55353076-f985-4a0c-bd1b-91ee727794fb")
    # get_dream_vote("55353076-f985-4a0c-bd1b-91ee727794fb")
    # update_dream(
    #     "55353076-f985-4a0c-bd1b-91ee727794fb",
    #     request_data=UpdateDreamRequest(name="name python"),
    # )
    # upvote_dream("55353076-f985-4a0c-bd1b-91ee727794fb")
    # downvote_dream("55353076-f985-4a0c-bd1b-91ee727794fb")
    # delete_dream("55353076-f985-4a0c-bd1b-91ee727794fb")

    # playlist
    # get_playlist("b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4")
    # update_playlist(
    #     "b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4",
    #     request_data=UpdatePlaylistRequest(name="name python"),
    # )
    # add_item_to_playlist(
    #     playlist_uuid="b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4",
    #     type=PlaylistItemType.DREAM,
    #     item_uuid="d20cad5c-b294-4094-a19d-f5ab043980ae",
    # )
    # delete_item_from_playlist(
    #     uuid="b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4", playlist_item_id=324
    # )
    # add_file_to_playlist(
    #     uuid="b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4",
    #     file_path="path_to_file/python_video.mp4",
    # )
    # delete_playlist("b9a643bd-f6d0-48ac-ba43-b10dcf4ecda4")

    # file
    # upload_file("path_to_file/python_video.mp4")
    pass


if __name__ == "__main__":
    run()
