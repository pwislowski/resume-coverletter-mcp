build application="baseline":
    uv run cv-mcp build {{application}}

format:
    uv run ruff check --fix .
    uv run ruff format .


check:
    uv run ruff check .
    uv run ruff format --check .
    uv run ty check
    uv run pytest
