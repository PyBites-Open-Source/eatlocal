"""command-line interface for eatlocal"""

import sys
from pathlib import Path

import typer
from rich import print
from rich.status import Status

from . import __version__
from .constants import EATLOCAL_HOME
from .eatlocal import (
    Bite,
    choose_bite,
    choose_local_bite,
    create_bite_dir,
    display_bite,
    download_bite,
    initialize_eatlocal,
    load_config,
    submit_bite,
    track_local_bites,
)

cli = typer.Typer(add_completion=False)


def report_version(display: bool) -> None:
    """Print version and exit."""
    if display:
        print(f"{Path(sys.argv[0]).name} {__version__}")
        raise typer.Exit()


@cli.callback()
def global_options(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        is_flag=True,
        is_eager=True,
        callback=report_version,
    ),
):
    """Download, extract, display, and submit PyBites code challenges."""


@cli.command()
def init(
    ctx: typer.Context,
) -> None:
    """Configure PyBites credentials and directory."""
    initialize_eatlocal()


@cli.command()
def download(
    ctx: typer.Context,
    clear: bool = typer.Option(
        False,
        "--clear-cache",
        "-C",
        is_flag=True,
        help="Clear the bites cache to fetch fresh bites.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-F",
        is_flag=True,
        help="Overwrite bite directory with a fresh version.",
    ),
) -> None:
    """Download and extract bite code from pybitesplatform.com."""
    config = load_config(EATLOCAL_HOME / ".env")
    bite = choose_bite(clear)
    with Status("Downloading bite..."):
        bite.platform_content = download_bite(bite, config)
        if bite.platform_content is None:
            return
    create_bite_dir(bite, config, force)
    track_local_bites(bite, config)


@cli.command()
def submit(
    ctx: typer.Context,
) -> None:
    """Submit a bite back to the PyBites Platform."""
    config = load_config(EATLOCAL_HOME / ".env")
    bite = choose_local_bite(config)
    submit_bite(
        bite,
        config,
    )


@cli.command()
def display(
    ctx: typer.Context,
    theme: str = typer.Option(
        "material",
        "--theme",
        "-t",
        help="Choose syntax highlighting for code.",
    ),
) -> None:
    """Read a bite directly in the terminal."""
    config = load_config(EATLOCAL_HOME / ".env")
    title, slug = choose_local_bite(config)
    bite = Bite(title, slug)
    display_bite(bite, config, theme=theme)


if __name__ == "__main__":
    cli()
