"""command-line interface for eatlocal"""

import sys
from pathlib import Path

import typer
from rich import print
from rich.prompt import Confirm
from rich.status import Status

from . import __version__
from .console import console
from .constants import EATLOCAL_HOME, ConsoleStyle
from .eatlocal import (
    Bite,
    choose_bite,
    choose_local_bite,
    create_bite_dir,
    display_bite,
    download_bite,
    get_credentials,
    install_browser,
    load_config,
    set_local_dir,
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
    """Configure PyBites credentials and repository."""
    while True:
        username, password = get_credentials()
        local_dir = set_local_dir()

        print(f"Your input - username: {username}, repo: {local_dir}.")
        if Confirm.ask(
            "Are these inputs correct? If you confirm, they will be stored under .eatlocal in your user home directory"
        ):
            break

    with Status("Initializing eatlocal..."):
        if not EATLOCAL_HOME.is_dir():
            EATLOCAL_HOME.mkdir()

        with open(EATLOCAL_HOME / ".env", "w", encoding="utf-8") as fh:
            fh.write(f"PYBITES_USERNAME={username}\n")
            fh.write(f"PYBITES_PASSWORD={password}\n")
            fh.write(f"PYBITES_REPO={local_dir}\n")
        with open(local_dir / ".local_bites.json", "w", encoding="utf-8") as fh:
            fh.write("{}")

    with Status("Installing browser..."):
        install_browser()


@cli.command()
def download(
    ctx: typer.Context,
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
    try:
        title, slug = choose_bite()
        bite = Bite(title, slug)
    except TypeError:
        console.print(
            ":warning: Unable to reach Pybites Platform.",
            style=ConsoleStyle.WARNING.value,
        )
        console.print(
            "Ensure internet connect is good and platform is avaiable.",
            style=ConsoleStyle.SUGGESTION.value,
        )
        return

    with Status("Downloading bite..."):
        bite.platform_content = download_bite(bite, config)
        if bite.platform_content is None:
            return
        track_local_bites(bite, config)
    create_bite_dir(bite, config, force)


@cli.command()
def submit(
    ctx: typer.Context,
) -> None:
    """Submit a bite back to the PyBites Platform."""
    config = load_config(EATLOCAL_HOME / ".env")
    title, slug = choose_local_bite(config)
    bite = Bite(title, slug)
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
