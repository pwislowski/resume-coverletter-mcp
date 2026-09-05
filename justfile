build application="baseline":
    uv run python scripts/build.py {{application}}

check:
    uv run pytest
