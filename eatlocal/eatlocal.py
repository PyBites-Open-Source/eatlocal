""" download and submit bites
"""


import webbrowser
from pathlib import Path
from time import sleep
from typing import Union
from zipfile import ZipFile, is_zipfile

from bs4 import BeautifulSoup
from git import GitCommandError, InvalidGitRepositoryError, Repo
from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import install
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .constants import BITE_URL, BITE_ZIPFILE, SUBMIT_URL
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

    path = Path(path or Path.cwd()).resolve()

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
    dest_path: Path,
    cache_path: str,
    delay: float = 1.0,
    verbose: bool = False,
) -> None:
    """Download bite ZIP archive file from the platform to the cache directory in the destination path.

    :bite_number: int The number of the bite to download.
    :username: str
    :password: str
    :delay: float Time in seconds to pause between operations
    :cache_path: Path for cached ZIP archive files
    :returns: None
    """

    try:
        cache_path = Path(dest_path / cache_path).resolve()
        path = find_cached_archive(bite_number, path=cache_path)
        print(f"Bite {bite_number} found: @ {path}")
        return
    except FileNotFoundError:
        pass

    cache_path = Path(dest_path / cache_path).resolve()
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
        print(
            f"[yellow]:warning: Bite {bite_number} was not downloaded. "
            "Ensure you are connected to the internet and your PyBites credentials are valid."
        )
        return

    if not is_zipfile(bite_ziparchive):
        print(
            f"[yellow]:warning: Bite {bite_number} is not a valid archive file.[/yellow]"
        )
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
    :dest_path: Path to extraction location.
    :cleanup: bool if False removes the downloaded zipfile.
    :cache_path: Path to search for ZIp archive.
    :force: bool if True overwrites the directory for the bite_number.
    :returns: None
    """

    try:
        cache_path = Path(dest_path / cache_path).resolve()
        bite = find_cached_archive(bite_number, path=cache_path)
    except FileNotFoundError as error:
        print(f"[yellow]:warning: Missing ZIP archive for bite {bite_number}: {error}")
        return

    dest_path = Path(dest_path).resolve() / str(bite_number)

    if dest_path.is_dir() and not force:
        print(
            f"[yellow]:warning: There already exists a directory for bite {bite_number}. "
            "Use the --force option to overwite."
        )
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
    bites_repo: Path,
    delay: float = 1.0,
    verbose: bool = False,
) -> None:
    """Submits bite by pushing to GitHub and then opens a browser for the
       bite page.

    :bite_number: int The number of the bite to submit.
    :username: str
    :password: str
    :bites_repo: Path Path to the github repository linked to PyBites.
    :delay: float Time in seconds to pause between operations.
    :returns: None
    """

    try:
        repo = Repo(bites_repo)
        repo.index.add(str(bite_number))
        repo.index.commit(f"submission Bite {bite_number} @ codechalleng.es")
    except InvalidGitRepositoryError:
        print(f"[yellow]:warning: Not a valid git repo: [/yellow]{bites_repo}")
        return
    except FileNotFoundError:
        print(
            f"[yellow]:warning: Seems like there is no bite {bite_number} to submit. "
            "Did you mean to submit a different bite?[/yellow]"
        )
        return

    try:
        repo.remotes.origin.push().raise_if_error()
    except GitCommandError:
        print(
            "[yellow]:warning: Unable to push to the remote PyBites repo.\n"
            f'Try navigating to your local repo @ [/yellow]{bites_repo}[yellow] and running the command "git push".\n'
            "Follow the advice from git.[/yellow]"
        )
        return

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
            print(
                "[yellow]:warning: Looks like you've already completed this bite![/yellow]"
            )
            break

        button.click()
        sleep(delay)

    webbrowser.open(bite_url)


def display_bite(
    bite_number: int,
    bite_repo: Path,
    theme: str,
) -> None:
    """Display the instructions provided in bite.html and display source code.

    :bite_number: int The number of the bite you want to read
    :bites_repo: Path Path to the github repository linked to PyBites.
    :theme: str
    :returns: None
    """

    path = Path(bite_repo).resolve() / str(bite_number)
    if not path.is_dir():
        print(
            f"[yellow]:warning: Unable to display bite {bite_number}. "
            f"Please make sure that path is correct and bite {bite_number} has been downloaded[/yellow]"
        )
        return

    html_file = path / list(path.glob("*.html"))[0]
    python_file = [
        file for file in list(path.glob("*.py")) if not file.name.startswith("test_")
    ][0]

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

    console = Console()
    console.print(layout)
