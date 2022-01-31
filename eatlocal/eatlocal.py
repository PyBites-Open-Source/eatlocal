from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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


def extract_bite(bite_number: int, cleanup: bool = True) -> None:
    """Extracts all the required files into a new directory
    named by the bite number.

    :bite_number: int The number of the bite you want to extract.
    :cleanup: bool if True removes the downloaded zipfile
    :returns: None
    """

    bite = BITE_ZIPFILE.format(bite_number=bite_number)

    try:
        with ZipFile(bite, "r") as zfile:
            zfile.extractall(f"./{bite_number}")
        print(f"Extracted bite {bite_number}")
        if cleanup:
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
        subprocess.run(
            ["git", "add", f"{bite_number}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        subprocess.run(
            ["git", "commit", f"-m'submission Bite {bite_number} @ codechalleng.es'"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        subprocess.run(
            ["git", "push"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

        print(f"\nPushed bite {bite_number} to github")

    except subprocess.CalledProcessError:
        print("Failed to push to GitHub")
        return

    driver = driver_setup()

    pybites_login(driver, username, password)

    print(f"Locating bite {bite_number} webpage.")

    driver.get(SUBMIT_URL.format(bite_number=bite_number))
    sleep(delay)

    buttons = {
        "githubDropdown": "Downloading code from GitHub.",
        "ghpull": None,
        "save": f"Submitting bite {bite_number}.",
    }

    for button_name, message in buttons.items():
        if message:
            print(message)
        button = driver.find_element(By.ID, button_name)
        button.click()
        sleep(delay)

    webbrowser.open(SUBMIT_URL)
