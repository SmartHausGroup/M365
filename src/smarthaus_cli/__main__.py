from __future__ import annotations

import json

import typer

from smarthaus_common.config import AppConfig
from smarthaus_common.errors import SmarthausError
from smarthaus_common.logging import configure_logging, get_logger
from smarthaus_graph.client import GraphClient

app = typer.Typer(add_completion=False, no_args_is_help=True, help="SmartHaus M365 CLI")
log = get_logger(__name__)


@app.callback()
def _init(verbose: bool = typer.Option(False, "--verbose", help="Verbose output")) -> None:
    configure_logging("DEBUG" if verbose else "INFO")


@app.command()
def health() -> None:
    """Simple CLI health check."""
    typer.echo("ok")


@app.command()
def org() -> None:
    """Fetch organization info from Graph (requires env credentials)."""
    try:
        cfg = AppConfig()
        client = GraphClient(cfg)
        data = client.get_organization()
        typer.echo(json.dumps(data, indent=2))
    except SmarthausError as e:
        log.error("%s", e)
        raise typer.Exit(code=2) from None


def main() -> None:
    app()


if __name__ == "__main__":
    main()
