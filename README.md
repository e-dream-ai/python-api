# edream-sdk

### local installation

If you need to setup locally to test or run code, follow [BUILD.md](BUILD.md) documentation.

### setup client

Initialize ApiClient and create a single instance to connect with backend, provide backend_url and api_key to ApiClient initialize function, an example on [run.py](run.py) file.

```python
from edream_sdk.client import create_edream_client

edream_client = create_edream_client(
    backend_url="http://localhost:8081/api/v1", api_key="your_api_key"
)

user = edream_client.get_logged_user()
print(user)
```

### run tests

run `run.py` file to test api client with this command

```bash
python tests/run.py
```
