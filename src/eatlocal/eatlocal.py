"""download and submit bites"""

import webbrowser
import requests
from os import environ, makedirs
from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup
from git import GitCommandError, InvalidGitRepositoryError, Repo
from playwright.sync_api import sync_playwright, Page
from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import install
from iterfzf import iterfzf

from .constants import BITE_URL, LOGIN_URL, EXERCISES_URL, FZF_DEFAULT_OPTS

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
    """Download bite ZIP archive file from the platform to the cache directory in the destination path.

    :bite_number: int The number of the bite to download.
    :username: str
    :password: str
    :delay: float Time in seconds to pause between operations
    :cache_path: Path for cached ZIP archive files
    :returns: None
    """

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
    bite_page = BITE_URL.format(bite_name=bites[bite_to_download])
    return bite_to_download, bite_page


def download_bite(
    bite: str,
    bite_page: str,
    dest_path: Path,
    verbose: bool = False,
    force: bool = False,
):
    bite_dir = bite_page.split("/")[-2].replace("-", "_")
    dest_path = Path(dest_path).resolve() / bite_dir
    print(dest_path)

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
    r = requests.get(bite_page)
    soup = BeautifulSoup(r.content, "html.parser")
    bite_description = soup.find(id="bite-description")
    code = soup.find(id="python-editor").text
    tests = soup.find(id="test-python-editor").text

    with open(dest_path / "bite.html", "w") as bite_html:
        for p in bite_description.find_all("p", {"class": "text-gray-700"})[-1]:
            bite_html.write(str(p).strip(" "))

    with open(dest_path / f"{bite_dir}.py", "w") as py_file:
        py_file.write(code)

    with open(dest_path / f"test_{bite_dir}.py", "w") as test_file:
        test_file.write(tests)


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
    # bite_url = SUBMIT_URL.format(bite_number=bite_number)
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

    console = Console()
    console.print(layout)
