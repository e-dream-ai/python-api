# AGENT.md — python-api (edream_sdk)

## Overview
Python SDK client for the infinidream.ai backend API. Used by video, engines, and electric-sheep-engine services.

## Stack
- **Language:** Python
- **HTTP:** requests
- **Serialization:** dataclasses-json, dacite
- **Build:** setuptools (setup.py + pyproject.toml)

## Project Structure
```
src/
  edream_sdk/     # Main package
    client.py     # API client (create_edream_client)
    ...
tests/
  gen.py          # Test script for dream generation
```

## Commands
```bash
pip install -r requirements.txt
pip install -e .                    # Install in editable mode
python tests/gen.py --algo deforum  # Test dream generation
```

## Installation
```bash
# From GitHub
pip install git+ssh://git@github.com/e-dream-ai/python-api.git

# Local development
git clone ... && cd python-api && pip install -e .
```

## Key Patterns
- `create_edream_client(base_url, api_key)` is the main entry point
- Client provides methods for dream CRUD, playlist management, and status polling
- Supports all algorithms: qwen-image, wan-t2v, wan-i2v, wan-i2v-lora, deforum, animatediff, uprez
