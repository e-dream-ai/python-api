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
