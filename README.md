# edream-sdk

the project and application has generally been renamed from e-dream to infinidream.
this module, however, has not yet been renamed.

### local installation

If you need to setup locally to test or run code, follow [BUILD.md](BUILD.md) documentation.

### simple example

Get an API key from your profile on the server, and store it in a .env file.
Then connect as follows:

```python
import os
from dotenv import load_dotenv
from edream_sdk.client import create_edream_client

API_KEY = os.getenv("API_KEY")
edream_client = create_edream_client(backend_url="https://api-alpha.infinidream.ai/api/v1", api_key=API_KEY)
user = edream_client.get_logged_user()
print(user)
```

### tests and more examples

There's a file to test api client:

```bash
python tests/run.py
```

this file has an example of every API call.
