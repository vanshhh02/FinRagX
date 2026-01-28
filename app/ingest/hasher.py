import hashlib

def hash_file(path: str) -> str:
    """Hash raw file bytes (stable, fast)."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()
