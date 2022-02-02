from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from rich import Layout, Live, Syntax, Panel
from bs4 import BeautifulSoup

from time import sleep
from zipfile import ZipFile

import os
import platform
import subprocess
import webbrowser

from .constants import BITE_URL, BITE_ZIPFILE, LOGIN_URL, SUBMIT_URL


def driver_setup() -> webdriver.Chrome:
    """Sets up a headless Chrome wedriver and returns it.

    :returns: webdriver.Chrome
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1920x1080")
    if platform.system() == "Windows":
        chrome_prefs = {"download.default_directory": os.getcwd()}
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


def download_bite(
    bite_number: int, username: str, password: str, delay: float = 1.5
) -> None:
    """Download bite .zip from the platform.

    :bite_number: int The number of the bite to download.
    :username: str
    :password: str
    :delay: float Time in seconds to pause between operations
    :returns: None
    """

    downloaded_bite = BITE_ZIPFILE.format(bite_number=bite_number)
    driver = driver_setup()
    pybites_login(driver, username, password)

    print(f"Retrieving bite {bite_number}")
    sleep(delay)

    driver.get(BITE_URL.format(bite_number=bite_number))
    sleep(delay)

    if os.path.exists(downloaded_bite):
        print(f"Bite {bite_number} successully downloaded to current directory")
    else:
        print(f"Bite {bite_number} was not downloaded")


def extract_bite(bite_number: int, keep_zip: bool = False) -> None:
    """Extracts all the required files into a new directory
    named by the bite number.

    :bite_number: int The number of the bite you want to extract.
    :keep_zip: bool if False removes the downloaded zipfile
    :returns: None
    """

    bite = BITE_ZIPFILE.format(bite_number=bite_number)

    try:
        with ZipFile(bite, "r") as zfile:
            zfile.extractall(f"./{bite_number}")
        print(f"Extracted bite {bite_number}")
        if not keep_zip:
            os.unlink(bite)

    except FileNotFoundError:
        print("No bite found.")


def submit_bite(
    bite_number: int, username: str, password: str, delay: float = 1.0
) -> None:
    """Submits bite by pushing to git hub and opening
    webbrowser to the bit page.

    :bite_number: int The number of the bite you want to submit.
    :username: str
    :password: str
    :delay: float Time in seconds to pause between operations
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


def read_bite(bite_number: int) -> None:
    """Display the instructions provided in bite.html and display source code.

    :bite_number: int The number of the bite you want to read
    :returns: None

    """
    
    layout = Layout()
    layout.spilt(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
    )
    layout['main'].split_row(
        Layout(name="directions"),
        Layout(name="code"),
    )

    with open(f"/home/helm/pybites/{bite_number}/bite.html", "r") as bite_html:
        soup = BeautifulSoup(bite_html, 'html_parser')
        instructions = soup.text

    
    with open(f"/home/helm/pybites/{bite_number}/") as code_file:
        code = Syntax(code_file.read(), "python", theme='material')

    layout["header"].update(Panel(f"Reading Bite {bite_number}", title='eatlocal'))
    layout['main']['directions'].update(Panel(instructions, title='Directions'))
    layout['main']['code'].update(Panel(code, title='Code'))


    with Live(layout, screen=True):
        input()

if __name__ == "__main__":
    read_bite(46)
