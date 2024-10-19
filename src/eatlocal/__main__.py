"""command-line interface for eatlocal"""

import sys
from pathlib import Path

import typer
from dotenv import dotenv_values
from rich import print
from rich.prompt import Confirm

from . import __version__
from .console import console
from .constants import EATLOCAL_HOME, SUCCESS, SUGGESTION, WARNING
from .eatlocal import (
    Bite,
    choose_bite,
    create_bite_dir,
    display_bite,
    download_bite,
    get_credentials,
    install_browser,
    set_repo,
    submit_bite,
)

cli = typer.Typer(add_completion=False)


def load_config(env_path: Path) -> dict[str, str]:
    """Load configuration from .env file.

    Args:
        env_path: Path to .env file.

    Returns:
        dict: Configuration variables.

    """
    config = {"PYBITES_USERNAME": "", "PYBITES_PASSWORD": "", "PYBITES_REPO": ""}
    if not env_path.exists():
        console.print(
            ":warning: Could not find or read .eatlocal/.env in your home directory.",
            style=WARNING,
        )
        console.print(
            "Please run [underline]eatlocal init[/underline] first.", style=SUGGESTION
        )
        sys.exit()
    config.update(dotenv_values(dotenv_path=env_path))
    return config


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
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        is_flag=True,
        help="Print each step as it happens.",
    ),
) -> None:
    """Configure PyBites credentials and repository."""
    while True:
        username, password = get_credentials()
        repo = set_repo()

        print(f"Your input - username: {username}, repo: {repo}.")
        if Confirm.ask(
            "Are these inputs correct? If you confirm, they will be stored under .eatlocal in your user home directory"
        ):
            break

    if not EATLOCAL_HOME.is_dir():
        EATLOCAL_HOME.mkdir()

    with open(EATLOCAL_HOME / ".env", "w", encoding="utf-8") as fh:
        fh.write(f"PYBITES_USERNAME={username}\n")
        fh.write(f"PYBITES_PASSWORD={password}\n")
        fh.write(f"PYBITES_REPO={repo}\n")

    if verbose:
        console.print(
            f"Successfully stored configuration variables under {EATLOCAL_HOME}.",
            style=SUCCESS,
        )
    install_browser(verbose)


@cli.command()
def download(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        is_flag=True,
        help="Print each step as it happens.",
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
    try:
        title, url = choose_bite(verbose)
        bite = Bite(title, url)
    except TypeError:
        console.print(":warning: Unable to reach Pybites Platform.", style=WARNING)
        console.print(
            "Ensure internet connect is good and platform is avaiable.",
            style=SUGGESTION,
        )
        return

    bite.platform_content = download_bite(config, bite, verbose)
    create_bite_dir(bite, config, verbose, force)


@cli.command()
def submit(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        is_flag=True,
        help="Print each step as it happens.",
    ),
) -> None:
    """Submit a bite back to the PyBites Platform."""
    config = load_config(EATLOCAL_HOME / ".env")
    try:
        title, url = choose_bite(verbose)
        bite = Bite(title, url)
    except TypeError:
        console.print(":warning: Unable to reach Pybites Platform.", style=WARNING)
        console.print(
            "Ensure internet connect is good and platform is avaliable.",
            style=SUGGESTION,
        )
    submit_bite(
        bite,
        config,
        verbose,
    )


@cli.command()
def display(
    ctx: typer.Context,
    bite: str,
    theme: str = typer.Option(
        "material",
        "--theme",
        "-t",
        help="Choose syntax highlighting for code.",
    ),
) -> None:
    """Read a bite directly in the terminal."""
    config = load_config(EATLOCAL_HOME / ".env")
    display_bite(bite, config, theme=theme)


if __name__ == "__main__":
    cli()
