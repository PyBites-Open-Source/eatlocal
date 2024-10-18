"""download and submit bites"""

import webbrowser
import requests
from dataclasses import dataclass
from os import environ, makedirs
from pathlib import Path

from bs4 import BeautifulSoup
from git import GitCommandError, InvalidGitRepositoryError, Repo
from playwright.sync_api import sync_playwright, Page
from rich import print
from rich.layout import Layout
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import install
from iterfzf import iterfzf
import install_playwright

from .constants import (
    BITE_URL,
    LOGIN_URL,
    EXERCISES_URL,
    FZF_DEFAULT_OPTS,
    WARNING,
    SUGGESTION,
    SUCCESS,
)
from .console import console

install(show_locals=True)


@dataclass
class Bite:
    title: str = None
    url: str = None
    platform_content: str = None

    def bite_url_to_dir(self, pybites_repo: Path) -> Path:
        bite_dir = self.url.split("/")[-2].replace("-", "_")
        return Path(pybites_repo).resolve() / bite_dir

    def fetch_local_code(self, config: dict) -> None:
        bite_dir = self.bite_url_to_dir(config["PYBITES_REPO"])
        if not bite_dir.is_dir():
            console.print(f":warning: Unable to submit: {self.title}.", style=WARNING)
            console.print(
                "Please make sure that path is correct and bite has been downloaded.",
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


def get_credentials() -> None:
    username = Prompt.ask("Enter your PyBites username")
    while True:
        password = Prompt.ask("Enter your PyBites user password", password=True)
        confirm_password = Prompt.ask("Confirm PyBites password", password=True)
        if password == confirm_password:
            break
        console.print(":warning: Password did not match.", style=WARNING)
    return username, password


def set_repo() -> None:
    repo = Path(
        Prompt.ask(
            "Enter the path to your local directory for PyBites, or press enter for the current directory",
            default=Path().cwd(),
            show_default=True,
        )
    ).expanduser()
    if not repo.exists():
        console.print(f":warning: The path {repo} could not be found!", style=WARNING)
        console.print("Make sure you have created a git repo for your bites", style=SUGGESTION)
    return repo


def install_browser(verbose: bool):
    if verbose:
        print("Installing browser...")
    with sync_playwright() as p:
        install_playwright.install(p.chromium)


def login(browser, username, password) -> Page:
    page: Page = browser.new_page()
    # only shorten for debugging, some bites need in e2e test need longer
    page.set_default_timeout(30000)
    page.goto(LOGIN_URL)

    page.click("#login-link")
    page.fill('input[name="login"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    return page


def choose_bite(
    verbose: bool = False,
) -> None:
    """Choose which bite will be downloaded."""
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
    environ["FZF_DEFAULT_OPTS"] = FZF_DEFAULT_OPTS
    bite_to_download = iterfzf(bites, multi=False)
    bite_url = BITE_URL.format(bite_name=bites[bite_to_download])
    return bite_to_download, bite_url


def download_bite(
    config: dict,
    bite: Bite,
    verbose: bool,
) -> str:
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            if verbose:
                print("Logging in...")
            page = login(
                browser,
                config["PYBITES_USERNAME"],
                config["PYBITES_PASSWORD"],
            )
            page.goto(bite.url)
            return page.content()


def create_bite_dir(
    bite: Bite,
    config: dict,
    verbose: bool = False,
    force: bool = False,
) -> None:
    dest_path = bite.bite_url_to_dir(config["PYBITES_REPO"])
    if dest_path.is_dir() and not force:
        print(
            f"[yellow]:warning: There already exists a directory for {bite.title}. "
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
    bite_description = soup.find(id="bite-description")
    code = soup.find(id="python-editor").text
    tests = soup.find(id="test-python-editor").text
    file_name = soup.find(id="filename").text

    with open(dest_path / "bite.html", "w") as bite_html:
        for p in bite_description.find_all("p", {"class": "text-gray-700"})[-1]:
            bite_html.write(str(p).strip(" "))

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
    """Submits bite then opens a browser for the bite page."""
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
            page.goto(bite.url)
            page.wait_for_url(bite.url)
            page.evaluate(
                f"""document.querySelector('.CodeMirror').CodeMirror.setValue({repr(bite.local_code)})"""
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
        console.print(":warning:Code did not pass the tests.", style=WARNING)

    if Confirm.ask(f"Would you like to open {bite.title} in your browser?"):
        webbrowser.open(bite.url)


def push_to_github(bite, bites_repo, verbose):
    if verbose:
        print("Tracking and commiting changes...")
    try:
        repo = Repo(bites_repo)
        repo.index.add(str(bite))
        repo.index.commit(f"Solved Bite: {bite}")
    except InvalidGitRepositoryError:
        print(f"[yellow]:warning: Not a valid git repo: [/yellow]{bites_repo}")
        return
    except FileNotFoundError:
        print(
            f"[yellow]:warning: Seems like there is no bite {bite} to submit. "
            "Did you mean to submit a different bite?[/yellow]"
        )
        return

    try:
        if verbose:
            print("Pushing changes...")
        repo.remotes.origin.push().raise_if_error()
    except GitCommandError:
        print(
            "[yellow]:warning: Unable to push to the remote PyBites repo.\n"
            f'Try navigating to your local repo @ [/yellow]{bites_repo}[yellow] and running the command "git push".\n'
            "Follow the advice from git.[/yellow]"
        )
        return

    console.print(f"\nPushed bite {bite} to github", style=SUCCESS)


def display_bite(
    bite: str,
    config: dict,
    theme: str,
) -> None:
    """Display the instructions provided in bite.html and display source code."""

    path = Path(config["PYBITES_REPO"]).resolve() / bite
    if not path.is_dir():
        console.print(f":warning: Unable to display bite {bite}.", style=WARNING)
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
        Panel(f"Displaying {bite} at {html_file}", title="eatlocal")
    )
    layout["main"]["directions"].update(Panel(instructions, title="Directions"))
    layout["main"]["code"].update(Panel(code, title="Code"))

    console.print(layout)
