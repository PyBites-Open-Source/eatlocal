"""download and submit bites"""

import json
import sys
import webbrowser
from dataclasses import dataclass
from datetime import timedelta
from os import environ, makedirs
from pathlib import Path

import install_playwright
import requests
import requests_cache
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from iterfzf import iterfzf
from playwright.sync_api import Page, sync_playwright
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.status import Status
from rich.syntax import Syntax
from rich.traceback import install

from .console import console
from .constants import (
    BITE_URL,
    CACHE_DB_LOCATION,
    BITES_API,
    EATLOCAL_HOME,
    FZF_DEFAULT_OPTS,
    LOCAL_BITES_DB,
    LOGIN_URL,
    PROFILE_URL,
    TIMEOUT_LENGTH,
    ConsoleStyle,
)

install(show_locals=True)
environ["FZF_DEFAULT_OPTS"] = FZF_DEFAULT_OPTS
requests_cache.install_cache(
    CACHE_DB_LOCATION, backend="sqlite", expire_after=timedelta(days=30)
)


@dataclass
class Bite:
    """Dataclass for a PyBites bite.

    Attributes:
        title: The title of the bite.
        slug: The slug of the bite.
        platform_content: The content of the bite downloaded from the platform.

    """

    title: str = None
    slug: str = None
    platform_content: str = None

    @property
    def url(self) -> str:
        return BITE_URL.format(bite_slug=self.slug)

    def bite_slug_to_dir(self, pybites_repo: Path) -> Path:
        return Path(pybites_repo).resolve() / self.slug

    def fetch_local_code(self, config: dict) -> None:
        bite_dir = self.bite_slug_to_dir(config["PYBITES_REPO"])
        if not bite_dir.is_dir():
            console.print(
                f":warning: Unable to find bite {self.title} locally.",
                style=ConsoleStyle.WARNING.value,
            )
            console.print(
                "Please make sure that your local pybites directory is correct and bite has been downloaded.",
                style=ConsoleStyle.SUGGESTION.value,
            )
            self.local_code = None
        else:
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
            style=ConsoleStyle.WARNING.value,
        )
        console.print(
            "Please run [underline]eatlocal init[/underline] first.",
            style=ConsoleStyle.SUGGESTION.value,
        )
        sys.exit()
    config.update(dotenv_values(dotenv_path=env_path))
    return config


def get_credentials() -> tuple[str, str]:
    """Prompt the user for their PyBites credentials.

    Returns:
        A tuple containing the user's PyBites username and password.

    """
    email = Prompt.ask("Enter your PyBites email address")
    while True:
        password = Prompt.ask("Enter your PyBites user password", password=True)
        confirm_password = Prompt.ask("Confirm PyBites password", password=True)
        if password == confirm_password:
            break
        console.print(
            ":warning: Password did not match.", style=ConsoleStyle.WARNING.value
        )
    return email, password


def set_local_dir() -> Path:
    """Set the local directory for PyBites.

    Returns:
        The path to the local directory where user's bites will be stored.

    """
    return Path(
        Prompt.ask(
            "Enter the path to your local directory for PyBites, or press enter for the current directory",
            default=Path().cwd(),
            show_default=True,
        )
    ).expanduser()


def install_browser() -> None:
    """Install the browser for the Playwright library.

    Returns:
        None

    """
    with sync_playwright() as p:
        install_playwright.install(p.chromium)


def initialize_eatlocal():
    use_existing = False
    if (EATLOCAL_HOME / ".env").is_file():
        with open(EATLOCAL_HOME / ".env", "r", encoding="utf-8") as fh:
            data = fh.read().splitlines()
        username = data[0].split("PYBITES_USERNAME=")[1].strip()
        password = data[1].split("PYBITES_PASSWORD=")[1].strip()
        local_dir = Path(data[2].split("PYBITES_REPO=")[1].strip())
        print(
            f"You have previously initialized eatlocal with the following:\nUsername: {username}\nDirectory: {local_dir}"
        )
        if Confirm.ask(
            "Would you like to use the same credentials and local directory?"
        ):
            use_existing = True

    if not use_existing:
        while True:
            username, password = get_credentials()
            local_dir = set_local_dir()
            print(
                f"Your input - username: {username}\nDirectory where bites will be stored: {local_dir}."
            )
            if Confirm.ask(
                "Are these inputs correct? If you confirm, they will be stored under .eatlocal in your user home directory"
            ):
                break

    with Status("Initializing eatlocal..."):
        if not EATLOCAL_HOME.is_dir():
            EATLOCAL_HOME.mkdir()

        with open(EATLOCAL_HOME / ".env", "w", encoding="utf-8") as fh:
            fh.write(f"PYBITES_USERNAME={username}\n")
            fh.write(f"PYBITES_PASSWORD={password}\n")
            fh.write(f"PYBITES_REPO={local_dir}\n")

    create_local_bites_db(local_dir)

    with Status("Installing browser..."):
        install_browser()
    console.print(":tada: Initialization complete.", style=ConsoleStyle.SUCCESS.value)


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


def create_local_bites_db(local_dir: Path) -> None:
    """Create the local bites database.

    Args:
        local_dir: Path to the local directory for PyBites.

    Returns:
        None

    """
    with Status("Creating local bites database..."):
        if (local_dir / ".local_bites.json").is_file():
            with open(local_dir / ".local_bites.json", "r", encoding="utf-8") as db:
                local_bites = json.load(db)
            with open(LOCAL_BITES_DB, "w", encoding="utf-8") as db:
                json.dump(local_bites, db)
            (local_dir / ".local_bites.json").unlink()

        if not LOCAL_BITES_DB.is_file():
            with open(LOCAL_BITES_DB, "w", encoding="utf-8") as fh:
                fh.write("{}")


def track_local_bites(bite: Bite, config: dict) -> None:
    """Track the bites that have been downloaded locally.

    Args:
        bite: Bite object containing the title and url of the bite.
        config: Dictionary containing the user's PyBites credentials.

    Returns:
        None

    """
    with open(LOCAL_BITES_DB, "r") as local_bites:
        bites = json.load(local_bites)
    bites[bite.title] = bite.slug
    with open(LOCAL_BITES_DB, "w") as local_bites:
        json.dump(bites, local_bites)


def choose_local_bite(config: dict) -> Bite:
    """Choose a local bite to submit.

    Args:
        config: Dictionary containing the user's PyBites credentials.

    Returns:
        A Bite object.

    """
    with open(Path(config["PYBITES_REPO"]) / ".local_bites.json", "r") as local_bites:
        bites = json.load(local_bites)
    bite = iterfzf(bites, multi=False)
    if bite is None:
        sys.exit()
    return Bite(bite, bites[bite])


def choose_bite(clear: bool = False) -> Bite:
    """Choose which bite will be downloaded.

    Returns:
        A Bite object.

    """
    if clear:
        requests_cache.clear()
    with Status("Retrieving bites..."):
        r = requests.get(BITES_API)
        if r.status_code != 200:
            console.print(
                ":warning: Unable to reach Pybites Platform.",
                style=ConsoleStyle.WARNING.value,
            )
            console.print(
                "Ensure internet connect is good and platform is avaiable.",
                style=ConsoleStyle.SUGGESTION.value,
            )
            sys.exit()
        bites = {bite["title"]: bite["slug"] for bite in r.json()}
    bite_to_download = iterfzf(bites, multi=False)
    if bite_to_download is None:
        sys.exit()
    slug = bites[bite_to_download]
    return Bite(bite_to_download, slug)


def download_bite(
    bite: Bite,
    config: dict,
) -> str | None:
    """Download the bite content from the PyBites platform.

    Args:
        config: Dictionary containing the user's PyBites credentials.
        bite: Bite object containing the title and url of the bite.

    Returns:
        The content of the bite from the platform.

    """
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            page = login(
                browser,
                config["PYBITES_USERNAME"],
                config["PYBITES_PASSWORD"],
            )
            if page.url != PROFILE_URL:
                console.print(
                    ":warning: Unable to login to PyBites.",
                    style=ConsoleStyle.WARNING.value,
                )
                console.print(
                    "Ensure your credentials are valid.",
                    style=ConsoleStyle.SUGGESTION.value,
                )
                sys.exit()
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
    force: bool = False,
) -> None:
    """Create a directory for the bite and write the bite content to it.

    Args:
        bite: Bite object.
        config: Dictionary containing the user's PyBites credentials.
        force: Whether to overwrite the directory if it already exists.

    Returns:
        None

    """
    dest_path = bite.bite_slug_to_dir(config["PYBITES_REPO"])
    if dest_path.is_dir() and not force:
        console.print(
            f":warning: There already exists a directory for {
                bite.title}.",
            style=ConsoleStyle.WARNING.value,
        )
        console.print(
            "Use the --force option to overwite.", style=ConsoleStyle.SUGGESTION.value
        )
        return

    soup = BeautifulSoup(bite.platform_content, "html.parser")

    bite_description = parse_bite_description(soup)
    try:
        code = soup.find(id="python-editor").text
        tests = soup.find(id="test-python-editor").text
        file_name = soup.find(id="filename").text.strip(".py")
    except AttributeError:
        console.print(
            f":warning: Unable to access {bite.title} content on the platform.",
            style=ConsoleStyle.WARNING.value,
        )
        console.print(
            "Please make sure that your credentials are valid and you have access to this bite.",
            style=ConsoleStyle.SUGGESTION.value,
        )
        sys.exit()

    try:
        makedirs(dest_path)
    except FileExistsError:
        pass
    with open(dest_path / "bite.html", "w") as bite_html:
        bite_html.write(bite_description)

    with open(dest_path / f"{file_name}.py", "w") as py_file:
        py_file.write(code)

    with open(dest_path / f"test_{file_name}.py", "w") as test_file:
        test_file.write(tests)
    console.print(
        f"Wrote {bite.title} to: {dest_path}", style=ConsoleStyle.SUCCESS.value
    )


def submit_bite(
    bite: str,
    config: dict,
) -> None:
    """Submit the bite to the PyBites platform.

    Args:
        bite: The name of the bite to submit.
        config: Dictionary containing the user's PyBites credentials.

    Returns:
        None

    """
    with Status("Submitting bite..."):
        bite.fetch_local_code(config)
        if bite.local_code is None:
            return

        with sync_playwright() as p:
            with p.chromium.launch() as browser:
                page = login(
                    browser,
                    config["PYBITES_USERNAME"],
                    config["PYBITES_PASSWORD"],
                )
                if page.url != PROFILE_URL:
                    console.print(
                        ":warning: Unable to login to PyBites.",
                        style=ConsoleStyle.WARNING.value,
                    )
                    console.print(
                        "Ensure your credentials are valid.",
                        style=ConsoleStyle.SUGGESTION.value,
                    )
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
        console.print(
            "Congrats, you passed this Bite!", style=ConsoleStyle.SUCCESS.value
        )
    else:
        console.print(
            ":warning: Code did not pass the tests.", style=ConsoleStyle.WARNING.value
        )

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
    path = bite.bite_slug_to_dir(config["PYBITES_REPO"])
    if not path.is_dir():
        console.print(
            f":warning: Unable to display bite {
                bite.title}.",
            style=ConsoleStyle.WARNING.value,
        )
        console.print(
            "Please make sure that path is correct and the bite has been downloaded.",
            style=ConsoleStyle.SUGGESTION.value,
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
