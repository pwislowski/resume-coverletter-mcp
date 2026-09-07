"""Signed artifact token helpers."""

import hashlib
import hmac
from pathlib import Path


def _artifact_key(artifact_id: str, secret: str) -> str:
    return hmac.new(secret.encode(), artifact_id.encode(), hashlib.sha256).hexdigest()


def sign_artifact(artifact_id: str, secret: str, expires: int) -> str:
    """Create a token containing no filesystem or application identifiers."""
    key = _artifact_key(artifact_id, secret)
    signature = hmac.new(
        secret.encode(), f"{expires}:{key}".encode(), hashlib.sha256
    ).hexdigest()
    return f"{expires}:{key}:{signature}"


def verify_artifact(token: str, secret: str, now: int) -> str:
    try:
        expires_text, key, signature = token.split(":", 2)
        expires = int(expires_text)
    except ValueError as exc:
        raise ValueError("Invalid download token") from exc
    if expires < now:
        raise ValueError("Download link expired")
    expected = hmac.new(
        secret.encode(), f"{expires}:{key}".encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid download token")
    if len(key) != 64 or any(char not in "0123456789abcdef" for char in key):
        raise ValueError("Invalid artifact identifier")
    return key


def resolve_artifact(root: Path, key: str, secret: str) -> Path:
    """Resolve an opaque key by scanning the bounded artifact store."""
    for path in root.rglob("*"):
        if path.name not in {"cv.pdf", "cover-letter.pdf"} and not (
            path.suffix == ".png" and path.stem.startswith(("cv-", "cover-letter-"))
        ):
            continue
        relative = path.relative_to(root).as_posix()
        if hmac.compare_digest(_artifact_key(relative, secret), key):
            resolved = path.resolve()
            if root.resolve() in resolved.parents:
                return resolved
    raise ValueError("Artifact not found")
