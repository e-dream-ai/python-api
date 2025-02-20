import os


def verify_file_path(file_path: str) -> None:
    if file_path is not None and not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: {file_path}")
