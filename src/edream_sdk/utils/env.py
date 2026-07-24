import os
import sys


def require_env(name: str) -> str:
    """Return a required environment variable, or exit with a clear error. """
    value = os.environ.get(name)
    if not value:
        print(f"Error: required environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)
    return value
