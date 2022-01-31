"""command-line interface for eatlocal

"""

import sys

from pathlib import Path

import typer

from .constants import USERNAME, PASSWORD
from .eatlocal import extract_bite, submit_bite, download_bite

from . import __version__


cli = typer.Typer(add_completion=False)


def report_version(display: bool) -> None:
    """Print version and exit."""
    if display:
        print(f"{Path(sys.argv[0]).name} {__version__}")
        raise typer.Exit()


@cli.command()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        is_flag=True,
        is_eager=True,
        callback=report_version,
    ),
    download: int = typer.Option(
        None,
        "--download",
        "-d",
        help="Download bite to current directory.",
    ),
    extract: int = typer.Option(
        None,
        "--extract",
        "-e",
        help="Extract ZIP file into current directory.",
    ),
    submit: int = typer.Option(
        None,
        "--submit",
        "-s",
        help="Submit bite.",
    ),
):
    """Download, extract and submit PyBites code challenges."""

    if sum(map(bool, [extract, submit, download])) != 1:
        print("Please specify only one of --extract, --submit or --download")
        raise typer.Exit(code=1)

    if extract:
        extract_bite(extract)
        raise typer.Exit()

    if submit:
        submit_bite(submit, USERNAME, PASSWORD)
        raise typer.Exit()

    if download:
        download_bite(download, USERNAME, PASSWORD)
        raise typer.Exit()


if __name__ == "__main__":
    cli()
