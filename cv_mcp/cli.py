"""Command-line interface for CV MCP."""

import typer

from cv_mcp import __version__
from cv_mcp.builder import build

app = typer.Typer(help="Build evidence-based CVs and cover letters.")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", callback=version_callback, is_eager=True
    ),
) -> None:
    """Build and serve the CV MCP application."""


@app.command("build")
def build_documents(
    slug: str = typer.Argument("baseline", help="Application slug."),
    json_output: bool = typer.Option(
        False, "--json", help="Emit machine-readable output."
    ),
):
    """Render a versioned CV and cover letter."""
    try:
        result = build(slug)
        if json_output:
            import json

            typer.echo(json.dumps(result or {"slug_id": slug}))
    except Exception as exc:
        typer.echo(f"Build failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@app.command()
def serve():
    """Run the Streamable HTTP MCP server."""
    from cv_mcp.server import run

    run()


if __name__ == "__main__":
    app()
