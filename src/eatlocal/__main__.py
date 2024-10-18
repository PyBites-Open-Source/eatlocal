"""command-line interface for eatlocal"""

import sys
from pathlib import Path

import typer
from dotenv import dotenv_values
from rich import print
from rich.prompt import Confirm, Prompt

from .console import console

from . import __version__
from .constants import EATLOCAL_HOME, SUGGESTION, WARNING, SUCCESS
from .eatlocal import (
    Bite,
    choose_bite,
    display_bite,
    create_bite_dir,
    submit_bite,
    download_bite,
)

cli = typer.Typer(add_completion=False)


def load_config(env_path: Path) -> dict[str, str]:
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
        username = Prompt.ask("Enter your PyBites username")
        while True:
            password = Prompt.ask("Enter your PyBites user password", password=True)
            confirm_password = Prompt.ask("Confirm PyBites password", password=True)
            if password == confirm_password:
                break
            print(":warning: Password did not match.", style=WARNING)

        repo = Path(
            Prompt.ask(
                "Enter the path to your local directory for PyBites, or press enter for the current directory",
                default=Path().cwd(),
                show_default=True,
            )
        ).expanduser()
        if not repo.exists():
            print(f":warning: The path {repo} could not be found!", style=WARNING)
            print(
                "Make sure you have created a git repo for your bites", style=SUGGESTION
            )

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

    print(
        f"Successfully stored configuration variables under {EATLOCAL_HOME}.",
        style=SUCCESS,
    )


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
    create_bite_dir(
        bite,
        config["PYBITES_REPO"],
        verbose,
        force,
    )


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
    """Submit a bite back to Codechalleng.es."""
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
