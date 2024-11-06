"""download and submit bites"""

import json
import sys
import webbrowser
from dataclasses import dataclass
from os import environ, makedirs
from pathlib import Path

import install_playwright
import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from iterfzf import iterfzf
from playwright.sync_api import Page, sync_playwright
from rich import print
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.traceback import install

from .console import console
from .constants import (
    BITE_URL,
    EXERCISES_URL,
    FZF_DEFAULT_OPTS,
    LOGIN_URL,
    PROFILE_URL,
    SUCCESS,
    SUGGESTION,
    TIMEOUT_LENGTH,
    WARNING,
)

install(show_locals=True)
environ["FZF_DEFAULT_OPTS"] = FZF_DEFAULT_OPTS


@dataclass
class Bite:
    """Dataclass for a PyBites bite.

    Attributes:
        title: The title of the bite.
        url: The url of the bite.
        platform_content: The content of the bite downloaded from the platform.

    """

    title: str = None
    url: str = None
    platform_content: str = None

    def bite_url_to_dir(self, pybites_repo: Path) -> Path:
        bite_dir = self.url.split("/")[-2].replace("-", "_")
        return Path(pybites_repo).resolve() / bite_dir

    def fetch_local_code(self, config: dict) -> None:
        bite_dir = self.bite_url_to_dir(config["PYBITES_REPO"])
        if not bite_dir.is_dir():
            console.print(
                f":warning: Unable to find bite {self.title} locally.",
                style=WARNING,
            )
            console.print(
                "Please make sure that your local pybites directory is correct and bite has been downloaded.",
                style=SUGGESTION,
            )
            return

        python_file = [
            file
            for file in list(bite_dir.glob("*.py"))
            if not file.name.startswith("test_")
        ][0]

        with open(python_file) as file:
            self.local_code = file.read()


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


def get_credentials() -> tuple[str, str]:
    """Prompt the user for their PyBites credentials.

    Returns:
        A tuple containing the user's PyBites username and password.

    """
    username = Prompt.ask("Enter your PyBites username")
    while True:
        password = Prompt.ask("Enter your PyBites user password", password=True)
        confirm_password = Prompt.ask("Confirm PyBites password", password=True)
        if password == confirm_password:
            break
        console.print(":warning: Password did not match.", style=WARNING)
    return username, password


def set_local_dir() -> str:
    """Set the local directory for PyBites.

    Returns:
        The path to the local directory where user's bites will be stored.

    """
    local_dir = Path(
        Prompt.ask(
            "Enter the path to your local directory for PyBites, or press enter for the current directory",
            default=Path().cwd(),
            show_default=True,
        )
    ).expanduser()
    if not local_dir.exists():
        console.print(
            f":warning: The path {
                local_dir} could not be found!",
            style=WARNING,
        )
        console.print(
            "Make sure you have created a local directory for your bites",
            style=SUGGESTION,
        )
    return local_dir


def install_browser(verbose: bool) -> None:
    """Install the browser for the Playwright library.

    Args:
        verbose: Whether to print additional information.

    Returns:
        None
    """
    if verbose:
        print("Installing browser...")
    with sync_playwright() as p:
        install_playwright.install(p.chromium)


def login(browser, username: str, password: str) -> Page:
    """Login to the PyBites platform.

    Args:
        browser: Playwright browser object.
        username: PyBites username.
        password: PyBites password.

    Returns:
        An authenticated page object for the PyBites platform.

    """
    page: Page = browser.new_page()
    # only shorten for debugging, some bites need in e2e test need longer
    page.set_default_timeout(TIMEOUT_LENGTH)
    page.goto(LOGIN_URL)

    page.click("#login-link")
    page.fill('input[name="login"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    return page


def track_local_bites(bite: Bite, config: dict) -> None:
    """Track the bites that have been downloaded locally.

    Args:
        bite: Bite object containing the title and url of the bite.
        config: Dictionary containing the user's PyBites credentials.

    Returns:
        None
    """
    with open(Path(config["PYBITES_REPO"]) / ".local_bites.json", "r") as local_bites:
        bites = json.load(local_bites)
    bites[bite.title] = bite.url
    with open(Path(config["PYBITES_REPO"]) / ".local_bites.json", "w") as local_bites:
        json.dump(bites, local_bites)


def choose_local_bite(config: dict) -> tuple[str, str]:
    """Choose a local bite to submit.

    Args:
        config: Dictionary containing the user's PyBites credentials.

    Returns:
        The name and url of the chosen bite.
    """
    with open(Path(config["PYBITES_REPO"]) / ".local_bites.json", "r") as local_bites:
        bites = json.load(local_bites)
    bite = iterfzf(bites, multi=False)
    return bite, bites[bite]


def choose_bite(
    verbose: bool = False,
) -> tuple[str, str]:
    """Choose which bite will be downloaded.

    Args:
        verbose: Whether to print additional information.

    Returns:
        The name and url of the chosen bite.

    """
    if verbose:
        print("Retrieving bites list...")
    r = requests.get(EXERCISES_URL)
    if r.status_code != 200:
        return
    soup = BeautifulSoup(r.content, "html.parser")
    rows = soup.table.find_all("tr")
    bites = {}
    for row in rows[1:]:
        try:
            bite = row.find_all("td")[1].a
            bite_name = bite.text
            bite_link = bite["href"]
            bites[bite_name] = bite_link
        except IndexError:
            continue
    bite_to_download = iterfzf(bites, multi=False)
    bite_url = BITE_URL.format(bite_name=bites[bite_to_download])
    return bite_to_download, bite_url


def download_bite(
    bite: Bite,
    config: dict,
    verbose: bool,
) -> str:
    """Download the bite content from the PyBites platform.

    Args:
        config: Dictionary containing the user's PyBites credentials.
        bite: Bite object containing the title and url of the bite.
        verbose: Whether to print additional information.

    Returns:
        The content of the bite from the platform.

    """
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            if verbose:
                print("Logging in...")
            page = login(
                browser,
                config["PYBITES_USERNAME"],
                config["PYBITES_PASSWORD"],
            )
            if page.url != PROFILE_URL:
                console.print(":warning: Unable to login to PyBites.", style=WARNING)
                console.print("Ensure your credentials are valid.", style=SUGGESTION)
                return
            page.goto(bite.url)
            return page.content()


def parse_bite_description(soup: BeautifulSoup) -> str:
    """Parse the bite description from the soup object.

    Args:
        soup: BeautifulSoup object containing the bite content.

    Returns:
        The bite description html as a string.

    """
    bite_description = soup.find(id="bite-description")
    write = False
    bite_description_str = ""
    for line in str(bite_description).splitlines():
        if 'id="filename"' in line:
            continue
        if write:
            bite_description_str += line + "\n"
        if """end author and learning paths""" in line:
            write = True
    return bite_description_str


def create_bite_dir(
    bite: Bite,
    config: dict,
    verbose: bool = False,
    force: bool = False,
) -> None:
    """Create a directory for the bite and write the bite content to it.

    Args:
        bite: Bite object.
        config: Dictionary containing the user's PyBites credentials.
        verbose: Whether to print additional information.
        force: Whether to overwrite the directory if it already exists.

    Returns:
        None

    """
    dest_path = bite.bite_url_to_dir(config["PYBITES_REPO"])
    if dest_path.is_dir() and not force:
        print(
            f"[yellow]:warning: There already exists a directory for {
                bite.title}. "
            "Use the --force option to overwite."
        )
        return

    try:
        makedirs(dest_path)
    except FileExistsError:
        pass

    if verbose:
        print("Parsing bite data...")
    soup = BeautifulSoup(bite.platform_content, "html.parser")

    bite_description = parse_bite_description(soup)
    code = soup.find(id="python-editor").text
    tests = soup.find(id="test-python-editor").text
    file_name = soup.find(id="filename").text.strip(".py")

    with open(dest_path / "bite.html", "w") as bite_html:
        bite_html.write(bite_description)

    with open(dest_path / f"{file_name}.py", "w") as py_file:
        py_file.write(code)

    with open(dest_path / f"test_{file_name}.py", "w") as test_file:
        test_file.write(tests)

    console.print(f"Wrote {bite.title} to: {dest_path}", style=SUCCESS)


def submit_bite(
    bite: str,
    config: dict,
    verbose: bool = False,
) -> None:
    """Submit the bite to the PyBites platform.

    Args:
        bite: The name of the bite to submit.
        config: Dictionary containing the user's PyBites credentials.
        verbose: Whether to print additional information.

    Returns:
        None

    """
    bite.fetch_local_code(config)
    if bite.local_code is None:
        return

    if verbose:
        print("Submitting bite...")
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            page = login(
                browser,
                config["PYBITES_USERNAME"],
                config["PYBITES_PASSWORD"],
            )
            if page.url != PROFILE_URL:
                console.print(":warning: Unable to login to PyBites.", style=WARNING)
                console.print("Ensure your credentials are valid.", style=SUGGESTION)
                return
            page.goto(bite.url)
            page.wait_for_url(bite.url)
            page.evaluate(
                f"""document.querySelector('.CodeMirror').CodeMirror.setValue({
                    repr(bite.local_code)})"""
            )
            page.click("#validate-button")
            page.wait_for_selector("#feedback", state="visible")
            page.wait_for_function(
                "document.querySelector('#feedback').innerText.includes('test session starts')"
            )

            validate_result = page.text_content("#feedback")
    if "Congrats, you passed this Bite" in validate_result:
        console.print("Congrats, you passed this Bite!", style=SUCCESS)
    else:
        console.print(":warning: Code did not pass the tests.", style=WARNING)

    if Confirm.ask(f"Would you like to open {bite.title} in your browser?"):
        webbrowser.open(bite.url)


def display_bite(
    bite: Bite,
    config: dict,
    theme: str,
) -> None:
    """Display the instructions and source code for a bite.

    Args:
        bite: The name of the bite to display.
        config: Dictionary containing the user's PyBites credentials.
        theme: The color theme for the code.

    Returns:
        None

    """
    path = bite.bite_url_to_dir(config["PYBITES_REPO"])
    if not path.is_dir():
        console.print(
            f":warning: Unable to display bite {
                bite.title}.",
            style=WARNING,
        )
        console.print(
            "Please make sure that path is correct and the bite has been downloaded.",
            style=SUGGESTION,
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
        Panel(f"Displaying {bite.title} at {html_file}", title="eatlocal")
    )
    layout["main"]["directions"].update(Panel(instructions, title="Directions"))
    layout["main"]["code"].update(Panel(code, title="Code"))

    console.print(layout)
