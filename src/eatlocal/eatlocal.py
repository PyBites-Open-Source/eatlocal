"""download and submit bites"""

import webbrowser
import requests
from os import environ, makedirs
from pathlib import Path

from bs4 import BeautifulSoup
from git import GitCommandError, InvalidGitRepositoryError, Repo
from playwright.sync_api import Page
from rich import print
from rich.layout import Layout
from rich.prompt import Confirm
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import install
from iterfzf import iterfzf

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


def _bite_url_to_dir(bite_url, pybites_repo):
    bite_dir = bite_url.split("/")[-2].replace("-", "_")
    bite_path = Path(pybites_repo).resolve() / bite_dir
    return bite_path


def download_bite(
    bite: str,
    bite_url: str,
    bite_content: str,
    pybites_repo: Path,
    verbose: bool = False,
    force: bool = False,
) -> None:
    dest_path = _bite_url_to_dir(bite_url, pybites_repo)
    if dest_path.is_dir() and not force:
        print(
            f"[yellow]:warning: There already exists a directory for {bite}. "
            "Use the --force option to overwite."
        )
        return

    try:
        makedirs(dest_path)
    except FileExistsError:
        pass

    if verbose:
        print("Parsing bite data...")
    soup = BeautifulSoup(bite_content, "html.parser")
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
    if verbose:
        print(f"Wrote {bite} to: {dest_path}", style=SUCCESS)


def submit_bite(
    bite: str,
    bite_url: str,
    pybites_repo: Path,
    page: Page,
    verbose: bool = False,
) -> None:
    """Submits bite then opens a browser for the bite page."""
    bite_dir = _bite_url_to_dir(bite_url, pybites_repo)
    # get code from bite_dir
    if not bite_dir.is_dir():
        console.print(f":warning: Unable to submit: {bite}.", style=WARNING)
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
        code = file.read()

    page.goto(bite_url)
    page.wait_for_url(bite_url)

    if verbose:
        print("Submitting bite...")
    page.evaluate(
        f"""document.querySelector('.CodeMirror').CodeMirror.setValue({repr(code)})"""
    )
    page.click("#validate-button")
    page.wait_for_selector("#feedback", state="visible")
    page.wait_for_function(
        "document.querySelector('#feedback').innerText.includes('test session starts')"
    )

    validate_result = page.text_content("#feedback")
    if "Congrats, you passed this Bite" in validate_result:
        print("Congrats, you passed this Bite!")
    else:
        print("Code did not pass the tests.")

    if Confirm.ask(f"Would you like to open {bite} in your browser?"):
        webbrowser.open(bite_url)


def push_to_github(bite, bites_repo, verbose):
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
        repo.remotes.origin.push().raise_if_error()
    except GitCommandError:
        print(
            "[yellow]:warning: Unable to push to the remote PyBites repo.\n"
            f'Try navigating to your local repo @ [/yellow]{bites_repo}[yellow] and running the command "git push".\n'
            "Follow the advice from git.[/yellow]"
        )
        return

    if verbose:
        print(f"\nPushed bite {bite} to github")


def display_bite(
    bite: str,
    bite_repo: Path,
    theme: str,
) -> None:
    """Display the instructions provided in bite.html and display source code.

    :bite_number: int The number of the bite you want to read
    :bites_repo: Path Path to the github repository linked to PyBites.
    :theme: str
    :returns: None
    """

    path = Path(bite_repo).resolve() / bite
    if not path.is_dir():
        print(
            f"[yellow]:warning: Unable to display bite {bite}. "
            f"Please make sure that path is correct and {bite} has been downloaded[/yellow]"
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
