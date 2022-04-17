""" download and submit bites
"""


import webbrowser
from pathlib import Path
from time import sleep
from typing import Union
from zipfile import ZipFile, is_zipfile

from bs4 import BeautifulSoup
from getkey import getkey, keys
from git import Repo
from rich import print
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import install
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .constants import BITE_REPO, BITE_URL, BITE_ZIPFILE, SUBMIT_URL
from .pydriver import driver_setup, pybites_login

install(show_locals=True)


def find_cached_archive(bite_number: int, path: Union[str, Path] = None) -> Path:
    """Return a Path for a PyBites bite zip archive in the given `path`.

    :bite_number: int
    :path: optional Path, resolved path defaults to current directory.
    :return: Path

    Raises:
    - FileNotFoundError if archive not found in the target path.
    """

    path = Path(path or Path.cwd())

    filename = BITE_ZIPFILE.format(bite_number=bite_number)

    try:
        archive = list(path.rglob(filename))[0]
    except IndexError:
        raise FileNotFoundError(filename) from None

    return archive.resolve()


def download_bite(
    bite_number: int,
    username: str,
    password: str,
    delay: float = 1.5,
    cache_path: Path = None,
    verbose: bool = False,
) -> None:
    """Download bite ZIP archive file from the platform to the current directory.

    :bite_number: int The number of the bite to download.
    :username: str
    :password: str
    :delay: float Time in seconds to pause between operations
    :cache_path: Path for cached ZIP archive files, defaults to current directory
    :returns: None
    """

    try:
        path = find_cached_archive(bite_number, path=cache_path)
        print(f"Bite {bite_number} found: @ {path}")
        return
    except FileNotFoundError:
        pass

    cache_path = Path(cache_path or Path.cwd()).resolve()
    cache_path.mkdir(mode=0o755, parents=True, exist_ok=True)

    if verbose:
        print(f"Retrieving bite {bite_number}...")
    sleep(delay)

    driver = driver_setup(cache_path)
    pybites_login(driver, username, password, verbose=verbose)
    driver.get(BITE_URL.format(bite_number=bite_number))
    sleep(delay)

    try:
        bite_ziparchive = find_cached_archive(bite_number, path=cache_path)
    except FileNotFoundError:
        print(f"[yellow]Bite {bite_number} was not downloaded.[/yellow]")
        return

    if not is_zipfile(bite_ziparchive):
        print(f"[yellow]Bite {bite_number} is not a valid archive file.[/yellow]")
        return

    if verbose:
        print(f"Bite {bite_number} successully downloaded: {bite_ziparchive}")


def extract_bite(
    bite_number: int,
    dest_path: Path = None,
    cleanup: bool = False,
    cache_path: Path = None,
    force: bool = False,
) -> None:
    """Extracts all the required files into a new directory
    named by the bite number.

    :bite_number: int The number of the bite you want to extract.
    :cleanup: bool if False removes the downloaded zipfile.
    :cache_path: Path to search for ZIp archive, defaults to current directory.
    :force: bool if True overwrites the directory for the bite_number.
    :returns: None
    """

    try:
        bite = find_cached_archive(bite_number, path=cache_path)
    except FileNotFoundError as error:
        print(f"[yellow]Missing ZIP archive for bite {bite_number}: {error}[/yellow]")
        return

    dest_path = Path(dest_path or Path.cwd()).resolve() / str(bite_number)

    if dest_path.is_dir() and not force:
        print(f"[yellow]There already exists a directory for bite {bite_number}. Use the --force flag to overwite.[/yellow]")
        return

    else:
        with ZipFile(bite, "r") as zipfile:
            zipfile.extractall(dest_path)

        print(f"Extracted bite {bite_number} @ {dest_path}")

        if cleanup:
            print(f"Cleaning up bite {bite_number} archive: {bite}")
            bite.unlink()


def submit_bite(
    bite_number: int,
    username: str,
    password: str,
    delay: float = 1.0,
    verbose: bool = False,
) -> None:
    """Submits bite by pushing to GitHub and then opens a browser for the
       bite page.

    :bite_number: int The number of the bite to submit.
    :username: str
    :password: str
    :delay: float time in seconds to pause between operations.
    :returns: None

    """

    repo = Repo(BITE_REPO)

    try:
        repo.index.add(str(bite_number))
    except FileNotFoundError:
        print(f"[yellow]Seems like there is no bite {bite_number} to submit. Did you mean to submit a different bite?\n[/yellow]")
        return

    repo.index.commit(f"submission Bite {bite_number} @ codechalleng.es")
    repo.remotes.origin.push().raise_if_error()
    if verbose:
        print(f"\nPushed bite {bite_number} to github")

    driver = driver_setup()

    pybites_login(driver, username, password, verbose=verbose)

    bite_url = SUBMIT_URL.format(bite_number=bite_number)

    driver.get(bite_url)
    sleep(delay)

    buttons = {
        "githubDropdown": "Downloading code from GitHub.",
        "ghpull": "",
        "save": f"Submitting bite {bite_number}.",
    }

    for button_name, message in buttons.items():
        if message:
            if verbose:
                print(message)
        try:
            button = driver.find_element(By.ID, button_name)
        except NoSuchElementException:
            print("[yellow]Looks like you've already completed this bite![/yellow]")
            break

        button.click()
        sleep(delay)

    webbrowser.open(bite_url)


def quit_display():
    """Quit the display"""
    quit_keys = ["q", "Q", keys.ESC]
    while True:
        key = getkey()
        if key in quit_keys:
            break


def display_bite(
    bite_number: int,
    bite_path: Path = BITE_REPO,
    theme: str = "material",
) -> None:
    """Display the instructions provided in bite.html and display source code.

    :bite_number: int The number of the bite you want to read
    :returns: None

    """

    path = Path(bite_path or Path.cwd()).resolve() / str(bite_number)

    html_file = path / list(path.glob("*.html"))[0]

    python_file = [file for file in list(path.glob("*.py")) if not file.name.startswith("test_")][0]

    with open(html_file, "r") as bite_html:
        soup = BeautifulSoup(bite_html, "html.parser")
        instructions = soup.text

    with open(python_file, "r") as code_file:
        code = Syntax(
            code_file.read(),
            "python",
            theme=theme,
            background_color="default",
        )

    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
    )
    layout["main"].split_row(
        Layout(name="directions"),
        Layout(name="code"),
    )

    layout["header"].update(
        Panel(f"Displaying Bite {bite_number} at {html_file}", title="eatlocal")
    )
    layout["main"]["directions"].update(Panel(instructions, title="Directions"))
    layout["main"]["code"].update(Panel(code, title="Code"))

    with Live(layout, screen=True):
        quit_display()
