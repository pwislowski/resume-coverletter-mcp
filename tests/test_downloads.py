from pathlib import Path

import pytest

from cv_mcp.downloads import resolve_artifact, sign_artifact, verify_artifact


def test_token_does_not_contain_server_path():
    token = sign_artifact("role/build-123/cv.pdf", "secret", 100)
    assert "/data/" not in token
    assert "role" not in token
    assert verify_artifact(token, "secret", 99) == token.split(":")[1]


def test_expired_token_rejected():
    token = sign_artifact("role/build-123/cv.pdf", "secret", 100)
    with pytest.raises(ValueError, match="expired"):
        verify_artifact(token, "secret", 101)


def test_tampered_token_rejected():
    token = sign_artifact("role/build-123/cv.pdf", "secret", 100)
    with pytest.raises(ValueError, match="Invalid download token"):
        verify_artifact(token[:-1] + ("0" if token[-1] != "0" else "1"), "secret", 99)


def test_opaque_key_resolves_only_allowlisted_artifact(tmp_path: Path):
    artifact = tmp_path / "role" / "build-123" / "cv.pdf"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"pdf")
    key = verify_artifact(
        sign_artifact("role/build-123/cv.pdf", "secret", 100), "secret", 99
    )
    assert resolve_artifact(tmp_path, key, "secret") == artifact
