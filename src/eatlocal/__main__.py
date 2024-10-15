"""command-line interface for eatlocal"""

import sys
from pathlib import Path
from time import sleep

import typer
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright, Page
from rich import print
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.status import Status

# from . import __version__
from .constants import EATLOCAL_HOME, EXERCISES_URL
from .eatlocal import login, choose_bite, display_bite, download_bite, submit_bite

console = Console()
cli = typer.Typer(add_completion=False)


def load_config(env_path: Path) -> dict[str, str]:
    config = {"PYBITES_USERNAME": "", "PYBITES_PASSWORD": "", "PYBITES_REPO": ""}
    if not env_path.exists():
        console.print(
            "[red]:warning: Could not find or read .eatlocal/.env in your home directory."
        )
        console.print("[yellow]Please run [underline]eatlocal init[/underline] first.")
        sys.exit()

    config.update(dotenv_values(dotenv_path=env_path))
    return config


# def report_version(display: bool) -> None:
#     """Print version and exit."""
#     if display:
#         print(f"{Path(sys.argv[0]).name} {__version__}")
#         raise typer.Exit()


# @cli.callback()
# def global_options(
#     ctx: typer.Context,
#     version: bool = typer.Option(
#         False,
#         "--version",
#         "-v",
#         is_flag=True,
#         is_eager=True,
#         callback=report_version,
#     ),
# ):
#     """Download, extract, display, and submit PyBites code challenges."""


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
            print("[yellow]:warning: Password did not match.")
        repo = Path(
            Prompt.ask(
                "Enter the path to your local git repo for PyBites, or press enter for the current directory",
                default=Path().cwd(),
                show_default=True,
            )
        ).expanduser()

        if not repo.exists():
            print(f"[yellow]:warning: The path {repo} could not be found!")

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

    print(f"[green]Successfully stored configuration variables under {EATLOCAL_HOME}.")


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
    """Download and extract bite code from Codechalleng.es.

    The bites are downloaded in a zip archive file and unzipped
    in the local git repository for PyBites. If the `cleanup` option is present
    the archive is deleted after extraction.
    """
    config = load_config(EATLOCAL_HOME / ".env")
    bite, bite_url = choose_bite(verbose)
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            page = login(
                browser,
                config["PYBITES_USERNAME"],
                config["PYBITES_PASSWORD"],
            )
            page.goto(bite_url)
            bite_content = page.content()
            download_bite(
                bite,
                bite_url,
                bite_content,
                config["PYBITES_REPO"],
                verbose,
                force,
            )


@cli.command()
def submit(
    ctx: typer.Context,
    bite_number: int,
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
    with Status(f"Submitting Bite {bite_number}"):
        submit_bite(
            bite_number,
            config["PYBITES_USERNAME"],
            config["PYBITES_PASSWORD"],
            config["PYBITES_REPO"],
            verbose=verbose,
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
    display_bite(bite, bite_repo=config["PYBITES_REPO"], theme=theme)


if __name__ == "__main__":
    cli()
