# edream-sdk

### variables

`BACKEND_URL` and `API_KEY` are configuration variables that determine the target environment for your API requests, are located on `client/api_client.py` file

target backend url

```python
BACKEND_URL = "http://localhost:8081/api/v1"
```

apikey to authorize backend requests

```python
API_KEY = "http://localhost:8081/api/v1"
```

### setup client

Initialize ApiClient and create a single instance to connect with backend, provide backend_url and api_key to ApiClient initialize function, an example on [run.py](run.py) file.

```python
from client.api_client import initialize_api_client

initialize_api_client(
    backend_url="http://localhost:8081/api/v1", api_key="your_api_key"
)
```

### run

run `run.py` file to test api client with this command

```bash
python run.py
```
