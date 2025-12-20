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

edream_client = create_edream_client(backend_url="https://api-alpha.infinidream.ai/api/v1",
                                     api_key=os.getenv("API_KEY"))
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

Generate dreams using AI algorithms:

```bash
# Available algorithms
python tests/gen.py --algo animatediff    # AnimateDiff video generation
python tests/gen.py --algo deforum        # Deforum video generation
python tests/gen.py --algo uprez          # Video upscaling
python tests/gen.py --algo qwen-image     # Qwen image generation
python tests/gen.py --algo wan-t2v         # Wan text-to-video generation
```

The script will create the dream, poll for completion, and display the video/image URL when ready.

### REST API

This Python SDK just wraps the servers' REST API. Its documentation
is served by swagger on
[staging](https://e-dream-76c98b08cc5d.herokuapp.com/api/v1/api-docs).
