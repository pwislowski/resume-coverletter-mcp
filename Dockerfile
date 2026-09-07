# syntax=docker/dockerfile:1
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_PROJECT_ENVIRONMENT=/opt/venv
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY cv_mcp ./cv_mcp
COPY templates ./templates
COPY README.md LICENSE ./
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --create-home app
RUN mkdir -p /data && chown -R app:app /app /data
USER app
EXPOSE 8000 8001
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["/opt/venv/bin/python", "-c", "import socket,urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health', timeout=2); socket.create_connection(('127.0.0.1',8000), timeout=2)"]
ENTRYPOINT ["/opt/venv/bin/python", "-m", "cv_mcp.cli"]
CMD ["serve"]
