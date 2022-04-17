"""command-line interface for eatlocal

"""

import sys
from collections import namedtuple
from pathlib import Path

import typer
from rich.status import Status

from . import __version__
from .constants import PASSWORD, USERNAME
from .eatlocal import display_bite, download_bite, extract_bite, submit_bite

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
    """Download, extract, and submit PyBites code challenges."""

    ctx.obj = GlobalOptions((USERNAME, PASSWORD))


@cli.command(name="download")
def download_subcommand(
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
) -> None:
    """Download and extract bite code from Codechalleng.es.

    The bites are downloaded in a zip archive file and unzipped
    in the current directory. If the `cleanup` option is present
    the archive is deleted after extraction.
    """
    with Status(f"Downloading Bite {bite_number}") as status:
        download_bite(bite_number, *ctx.obj.creds, cache_path="cache", verbose=verbose)
        status.update(f"Extracting Bite {bite_number}")
        extract_bite(bite_number, cleanup=cleanup, cache_path="cache", force=force)


@cli.command(name="submit")
def submit_subcommand(
    ctx: typer.Context,
    bite_number: int,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        is_flag=True,
        help="Print each step as it happens",
    ),
) -> None:
    """Submit a bite back to Codechalleng.es."""

    with Status(f"Submitting Bite {bite_number}"):
        submit_bite(bite_number, *ctx.obj.creds, verbose=verbose)


@cli.command(name="display")
def read_subcommand(
    ctx: typer.Context,
    bite_number: int,
    bite_path: Path = None,
    theme: str = typer.Option(
        "material",
        "--theme",
        "-t",
        is_flag=True,
        help="Choose syntax highlighting for code.",
    ),
) -> None:
    """Read a bite directly in the terminal."""

    display_bite(bite_number, theme=theme)


if __name__ == "__main__":
    cli()
