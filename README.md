# edream-sdk

copyright (c) 2025 e-dream, inc

the project and application has generally been renamed from e-dream to
infinidream. this module, however, has not yet been renamed, but it
works fine with the current servers.

### local installation

If you need to setup locally to test or run code, follow
[BUILD.md](BUILD.md) documentation.


### simple example

Get an API key from your profile on the server, and store it in a .env
file. Then connect as follows:

```python
import os
from dotenv import load_dotenv
from edream_sdk.client import create_edream_client

load_dotenv()

edream_client = create_edream_client(
    backend_url=os.getenv("BACKEND_URL", "https://api-alpha.infinidream.ai/api/v1"),
    api_key=os.getenv("API_KEY")
)
user = edream_client.get_logged_user()
print(user)
```

### tests and more examples

There's a file to test api client:

```bash
python tests/run.py
```

this file has an example of every API call.

### playlists and keyframes

Add many items to a playlist in one atomic request. The whole batch
succeeds or nothing does, and the backend rejects it outright if any item
is already on the playlist, so filter first:

```python
from edream_sdk.types.playlist_types import PlaylistItemType

playlist = edream_client.get_playlist(playlist_uuid)
already = {i["dreamItem"]["uuid"] for i in playlist["items"] if i.get("dreamItem")}

added = edream_client.add_items_to_playlist(playlist_uuid, [
    {"type": PlaylistItemType.DREAM, "uuid": uuid}
    for uuid in dream_uuids if uuid not in already
])
```

At most 500 items per call. For a single item `add_item_to_playlist` is
still the simpler choice.

Keyframes can be looked up by name rather than scanned for:

```python
keyframe = edream_client.find_keyframe_by_name("00248=22588")

# or page through matches yourself -- search is a substring match
page = edream_client.get_keyframes(search="00248=", take=100)
print(page["count"], "matches")
```

### AI generation

Use the [Quick Start](https://docs.google.com/document/d/1sXfGgogyrDyaOOxCyG6uvkG1l6uTUE2iNdkqVAa-N0Q).

Set `DREAM_UUID` (a processed video dream) and `STILL_UUID` (a processed image dream) in your `.env`. See `.env.example`.

```bash
python tests/gen.py --algo ltx-i2v     # single algorithm
python tests/gen.py --all              # smoke test every endpoint
python tests/gen.py --all --timeout 7200
```

Available algorithms: `animatediff`, `deforum`, `wan-t2v`, `wan-i2v`, `wan-i2v-lora`, `ltx-i2v`, `qwen-image`, `z-image-turbo`, `uprez`, `nvidia-uprez`

For batch/playlist workflows see [engines](https://github.com/e-dream-ai/engines).

### REST API

This Python SDK just wraps the servers' REST API. Its documentation
is served by swagger on
[staging](https://e-dream-76c98b08cc5d.herokuapp.com/api/v1/api-docs).
