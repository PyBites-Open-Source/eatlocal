"""command-line interface for eatlocal

"""

import sys
from collections import namedtuple
from pathlib import Path

import typer
from rich import print
from rich.prompt import Confirm, Prompt
from rich.status import Status

from . import __version__
from .constants import EATLOCAL_HOME, REPO_WARNING, config
from .eatlocal import display_bite, download_bite, extract_bite, submit_bite


def check_for_pybites_repo(bites_repo):
    if not bites_repo:
        print(REPO_WARNING)
        sys.exit()
        

cli = typer.Typer(add_completion=False)


def report_version(display: bool) -> None:
    """Print version and exit."""
    if display:
        print(f"{Path(sys.argv[0]).name} {__version__}")
        raise typer.Exit()


GlobalOptions = namedtuple("GlobalOptions", "creds")


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

    ctx.obj = GlobalOptions((config["PYBITES_USERNAME"], config["PYBITES_PASSWORD"]))


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
    """Configure PyBites credentials."""
    while True:
        username = Prompt.ask("Enter your PyBites username")
        password = Prompt.ask("Enter your PyBites user password", password=True)
        repo = Prompt.ask("Enter the path to your local git repo for PyBites", default=Path().cwd(), show_default=True)

        print(f"Your input - username: {username}, password: {password}, repo: {repo}.")
        if Confirm.ask("Are these inputs correct? If you confirm, they will be stored under .eatlocal in your user home directory"):
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
    bite_number: int,
    cleanup: bool = typer.Option(
        False,
        "--cleanup",
        "-C",
        is_flag=True,
        help="Remove downloaded bite archive file.",
    ),
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
    bites_repo: Path = typer.Option(
        config["PYBITES_REPO"],
        "-R",
        "--repo",
        help="Path to PyBites repository.",
    ),
) -> None:
    """Download and extract bite code from Codechalleng.es.

    The bites are downloaded in a zip archive file and unzipped
    in the path provided, defaults to $PYBITES_REPO. If the `cleanup` option is present
    the archive is deleted after extraction.
    """
    check_for_pybites_repo(bites_repo)
    with Status(f"Downloading Bite {bite_number}") as status:
        download_bite(
            bite_number,
            *ctx.obj.creds,
            cache_path="cache",
            dest_path=bites_repo,
            verbose=verbose,
        )
        status.update(f"Extracting Bite {bite_number}")
        extract_bite(
            bite_number,
            cleanup=cleanup,
            cache_path="cache",
            dest_path=bites_repo,
            force=force,
        )


@cli.command()
def submit(
    ctx: typer.Context,
    bite_number: int,
    bites_repo: Path = typer.Option(
        config["PYBITES_REPO"],
        "--repo",
        "-R",
        help="Path to PyBites repo.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        is_flag=True,
        help="Print each step as it happens.",
    ),
) -> None:
    """Submit a bite back to Codechalleng.es."""
    check_for_pybites_repo(bites_repo)
    with Status(f"Submitting Bite {bite_number}"):
        submit_bite(bite_number, *ctx.obj.creds, bites_repo=bites_repo, verbose=verbose)


@cli.command()
def display(
    ctx: typer.Context,
    bite_number: int,
    bites_repo: Path = typer.Option(
        config["PYBITES_REPO"],
        "--repo",
        "-R",
        help="Path to bite directory.",
    ),
    theme: str = typer.Option(
        "material",
        "--theme",
        "-t",
        help="Choose syntax highlighting for code.",
    ),
) -> None:
    """Read a bite directly in the terminal."""
    check_for_pybites_repo(bites_repo)
    display_bite(bite_number, bite_path=bites_repo, theme=theme)


if __name__ == "__main__":
    cli()
