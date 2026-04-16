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

### AI generation

Set `DREAM_UUID` (a processed video dream) and `STILL_UUID` (a processed image dream) in your `.env` for endpoints that require existing content. See `.env.example`.

Run a single algorithm:

```bash
python tests/gen.py --algo wan-t2v         # text-to-video
python tests/gen.py --algo wan-i2v         # image-to-video (requires STILL_UUID)
python tests/gen.py --algo wan-i2v-lora    # image-to-video with LoRA (requires STILL_UUID)
python tests/gen.py --algo ltx-i2v         # LTX image-to-video (requires STILL_UUID)
python tests/gen.py --algo qwen-image      # image generation
python tests/gen.py --algo z-image-turbo   # fast image generation
python tests/gen.py --algo uprez           # video upscaling (requires DREAM_UUID)
python tests/gen.py --algo nvidia-uprez    # NVIDIA video upscaling (requires DREAM_UUID)
python tests/gen.py --algo animatediff     # AnimateDiff video generation
python tests/gen.py --algo deforum         # Deforum video generation
```

Or smoke test every endpoint at once:

```bash
python tests/gen.py --all
python tests/gen.py --all --timeout 7200
```

The script submits one job per algorithm, polls for completion, and prints the result URL.

### REST API

This Python SDK just wraps the servers' REST API. Its documentation
is served by swagger on
[staging](https://e-dream-76c98b08cc5d.herokuapp.com/api/v1/api-docs).
