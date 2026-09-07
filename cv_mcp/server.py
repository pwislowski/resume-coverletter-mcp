"""MCP adapter for the private CV builder.

The server deliberately exposes career evidence as read-only. Draft persistence is
filesystem-backed and scoped to the configured applications directory.
"""

import mimetypes
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

import structlog
import yaml
from mcp.server import MCPServer

from cv_mcp.builder import build
from cv_mcp.config import Settings
from cv_mcp.downloads import resolve_artifact, sign_artifact, verify_artifact
from cv_mcp.logging import setup_logging

settings = Settings()
setup_logging(settings.log_level)
logger = structlog.get_logger(__name__)
settings.ensure_runtime()

logger.info(
    "server_configured",
    profile=str(settings.profile),
    applications=str(settings.applications),
)

mcp = MCPServer(
    "CV Builder",
    instructions=(
        "Use get_career_profile first. Save a tailored application draft, then "
        "build it. Builds are previews ready for human factual and layout review."
    ),
)


def _read_yaml(path: Path):
    return yaml.safe_load(path.read_text())


def _job_app_slug_guardrail(slug: str):
    if not slug or not slug.replace("-", "").isalnum() or slug.startswith("-"):
        raise ValueError("Invalid application slug")


@mcp.tool()
def get_career_profile() -> dict:
    """Read the authoritative career evidence and review notes."""
    logger.info("tool_called", tool="get_career_profile")
    return _read_yaml(settings.profile)


@mcp.tool()
def list_applications() -> list[dict]:
    """List saved application drafts."""
    logger.info("tool_called", tool="list_applications")
    result = []
    files = settings.applications.glob("*/application.yaml")
    for path in sorted(files):
        result.append({"id": path.parent.name, "path": str(path.name)})
    return result


@mcp.tool()
def get_application(slug: str) -> dict:
    """Read one application draft by lowercase slug."""

    _job_app_slug_guardrail(slug)
    logger.info("tool_called", tool="get_application", slug=slug)

    path = settings.applications / slug / "application.yaml"
    if not path.is_file():
        raise ValueError("Application not found")
    return _read_yaml(path)


@mcp.tool()
def save_application(slug: str, content: dict) -> dict:
    """Save a draft application; content is validated by the builder on build."""
    _job_app_slug_guardrail(slug)
    logger.info("tool_called", tool="save_application", slug=slug)

    target = settings.applications / slug / "application.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(content, sort_keys=False, allow_unicode=True))
    return {"id": slug, "saved": True}


@mcp.tool()
def start_build(slug: str, idempotency_key: str = "") -> dict:
    """Build a saved application and return its result."""
    if not idempotency_key.strip():
        raise ValueError("idempotency_key is required")
    logger.info("build_started", slug=slug)
    result = build(slug)
    logger.info("build_succeeded", slug=slug)
    return {"id": slug, "status": "succeeded", "result": result}


@mcp.tool()
def get_download_links(build_path: str) -> dict:
    """Issue short-lived links for the PDF artifacts in a successful build."""
    logger.info("tool_called", tool="get_download_links")
    if not settings.download_base_url or not settings.download_signing_secret:
        raise ValueError("Download service is not configured")
    root = settings.output.resolve()
    path = Path(build_path).resolve()
    if root not in path.parents:
        raise ValueError("Build path is outside the artifact store")
    links = {}
    expires = int(time.time()) + 1800
    for name in ("cv.pdf", "cover-letter.pdf"):
        artifact = path / name
        if artifact.is_file():
            artifact_id = artifact.relative_to(root).as_posix()
            token = sign_artifact(
                artifact_id, settings.download_signing_secret, expires
            )
            links[name] = (
                f"{settings.download_base_url.rstrip('/')}/download/{quote(token, safe='')}"
            )
    logger.info("download_links_issued", artifact_count=len(links), expires_at=expires)
    return {"expires_at": expires, "links": links}


def _download_server() -> ThreadingHTTPServer:
    root = settings.output.resolve()
    secret = settings.download_signing_secret

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                logger.info("health_check", endpoint="download")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")
                return
            token = unquote(urlparse(self.path).path.removeprefix("/download/"))
            try:
                artifact_key = verify_artifact(token, secret, int(time.time()))
                artifact = resolve_artifact(root, artifact_key, secret)
                data = artifact.read_bytes()
            except (ValueError, OSError):
                logger.warning("download_rejected")
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header(
                "Content-Type",
                mimetypes.guess_type(artifact.name)[0] or "application/octet-stream",
            )
            self.send_header("Content-Length", str(len(data)))
            self.send_header(
                "Content-Disposition", f'attachment; filename="{artifact.name}"'
            )
            self.send_header("Cache-Control", "private, no-store")
            self.end_headers()
            self.wfile.write(data)
            logger.info("download_served", artifact=artifact.name, bytes=len(data))

        def log_message(self, format: str, *args: object) -> None:
            return

    return ThreadingHTTPServer(("0.0.0.0", 8001), Handler)


def run() -> None:
    """Run on the internal container interface."""
    logger.info("server_starting", mcp_port=8000, download_port=8001)
    download_server = _download_server() if settings.download_signing_secret else None
    download_thread = None
    if download_server:
        download_thread = threading.Thread(target=download_server.serve_forever)
        download_thread.start()
    try:
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
    finally:
        if download_server:
            logger.info("download_server_stopping")
            download_server.shutdown()
            download_server.server_close()
        if download_thread:
            download_thread.join(timeout=5)
        logger.info("server_stopped")
