"""Security related helpers (placeholder for future auth, API keys, etc.)."""
import hashlib


def hash_code(code: str) -> str:
    """Return a stable SHA-256 hash of a code snippet (useful for dedup/caching)."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()
