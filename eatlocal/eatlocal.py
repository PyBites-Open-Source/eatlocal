""" download and submit bites

"""

import subprocess
import webbrowser

from pathlib import Path
from time import sleep
from typing import Union
from zipfile import ZipFile, is_zipfile

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from rich.layout import Layout
from rich.live import Live
from rich.syntax import Syntax
from rich.panel import Panel

from bs4 import BeautifulSoup

from .constants import BITE_URL, BITE_ZIPFILE, LOGIN_URL, SUBMIT_URL


def driver_setup(path: Union[str, Path] = None) -> webdriver.Chrome:
    """Configures a headless Chrome wedriver and returns it.

    If a path is given, it's used to set the driver's default download
    directory.

    :path: Union[str, Path]
    :returns: configured webdriver.Chrome
    """

    path = str(Path(path or Path.cwd()).resolve())

    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1920x1080")
    chrome_prefs = {"download.default_directory": path}
    options.experimental_options["prefs"] = chrome_prefs

    return webdriver.Chrome(options=options)


def pybites_login(driver: webdriver.Chrome, username: str, password: str) -> None:
    """Authenticate this driver instance with the given credentials.

    :driver: webdriver.Chrome
    :username: str
    :password: str
    :returns: None
    """

    print("Logging into PyBites")
    driver.get(LOGIN_URL)

    username_field = driver.find_element(By.ID, "id_username")
    username_field.send_keys(username)
    password_field = driver.find_element(By.ID, "id_password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)


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
        print(f"Bite {bite_number} found: {path}")
        return
    except FileNotFoundError:
        pass

    cache_path = Path(cache_path or Path.cwd()).resolve()
    cache_path.mkdir(mode=0o755, parents=True, exist_ok=True)

    print(f"Retrieving bite {bite_number}...")
    sleep(delay)

    driver = driver_setup(cache_path)
    pybites_login(driver, username, password)
    driver.get(BITE_URL.format(bite_number=bite_number))
    sleep(delay)

    try:
        bite_ziparchive = find_cached_archive(bite_number, path=cache_path)
    except FileNotFoundError:
        print(f"Bite {bite_number} was not downloaded.")
        return

    if not is_zipfile(bite_ziparchive):
        print(f"Bite {bite_number} is not a valid archive file.")
        return

    print(f"Bite {bite_number} successully downloaded: {bite_ziparchive}")


def extract_bite(
    bite_number: int,
    dest_path: Path = None,
    cleanup: bool = False,
    cache_path: Path = None,
) -> None:
    """Extracts all the required files into a new directory
    named by the bite number.

    :bite_number: int The number of the bite you want to extract.
    :cleanup: bool if False removes the downloaded zipfile.
    :cache_path: Path to search for ZIp archive, defaults to current directory.
    :returns: None
    """

    try:
        bite = find_cached_archive(bite_number, path=cache_path)
    except FileNotFoundError as error:
        print(f"Missing ZIP archive for bite {bite_number}: {error}")
        return

    dest_path = Path(dest_path or Path.cwd()).resolve() / str(bite_number)

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
) -> None:
    """Submits bite by pushing to GitHub and then opens a browser for the
       bite page.

    :bite_number: int The number of the bite to submit.
    :username: str
    :password: str
    :delay: float time in seconds to pause between operations.
    :returns: None

    """

    try:
        git_commands = [
            ["git", "add", f"{bite_number}"],
            ["git", "commit", f"-m'submission Bite {bite_number} @ codechalleng.es'"],
            ["git", "push"],
        ]

        for command in git_commands:
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

        print(f"\nPushed bite {bite_number} to github")

    except subprocess.CalledProcessError:
        print("Failed to push to GitHub")
        return

    driver = driver_setup()

    pybites_login(driver, username, password)

    bite_url = SUBMIT_URL.format(bite_number=bite_number)

    print(f"Locating bite {bite_number} webpage")

    driver.get(bite_url)
    sleep(delay)

    buttons = {
        "githubDropdown": "Downloading code from GitHub.",
        "ghpull": "",
        "save": f"Submitting bite {bite_number}.",
    }

    for button_name, message in buttons.items():
        if message:
            print(message)
        try:
            button = driver.find_element(By.ID, button_name)
        except NoSuchElementException as error:
            print("Looks like you've already completed this bite!")
            break

        button.click()
        sleep(delay)

    webbrowser.open(bite_url)


def display_bite(
    bite_number: int,
    bite_path: Path = None,
    theme: str = "material",
) -> None:
    """Display the instructions provided in bite.html and display source code.

    :bite_number: int The number of the bite you want to read
    :returns: None

    """

    path = Path(bite_path or Path.cwd()).resolve() / str(bite_number)

    html_file = path / list(path.glob('*.html'))[0]

    for file in path.iterdir():
        if str(file).endswith(".py") and not str(file.parts[-1]).startswith("test_"):
            python_file = file

    with open(html_file, "r") as bite_html:
        soup = BeautifulSoup(bite_html, "html.parser")
        instructions = soup.text

    with open(path / python_file, "r") as code_file:
        code = Syntax(code_file.read(), "python", theme=theme)

    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
    )
    layout["main"].split_row(
        Layout(name="directions"),
        Layout(name="code"),
    )

    layout["header"].update(Panel(f"Displaying Bite {bite_number} at {html_file}", title="eatlocal"))
    layout["main"]["directions"].update(Panel(instructions, title="Directions"))
    layout["main"]["code"].update(Panel(code, title="Code"))

    with Live(layout, screen=True):
        input()
