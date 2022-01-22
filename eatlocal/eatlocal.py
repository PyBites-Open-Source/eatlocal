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


def driver_setup():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1920x1080")
    if platform.system() == "Windows":
        chrome_prefs = {"download.default_directory": os.getcwd()}
        options.experimental_options["prefs"] = chrome_prefs
    return webdriver.Chrome(options=options)


def pybites_login(driver, username, password):
    login_url = "https://codechalleng.es/login"
    print("Logging into PyBites")
    driver.get(login_url)
    username_field = driver.find_element(By.ID, "id_username")
    username_field.send_keys(username)
    password_field = driver.find_element(By.ID, "id_password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)


def download_bite(bite_number, username, password):
    """Download bite .zip from the platform.

    :bite_number: The number of the bite you want to download.
    :returns: None
    """

    downloaded_bite = f"pybites_bite{bite_number}.zip"
    driver = driver_setup()
    pybites_login(driver, username, password)

    print(f"Retrieving bite {bite_number}")
    sleep(1.5)
    bite_url = f"https://codechalleng.es/bites/api/downloads/bites/{bite_number}"
    driver.get(bite_url)
    sleep(1.5)
    if os.path.exists(downloaded_bite):
        print(f"Bite {bite_number} successully downloaded to current directory")
        extract_bite(bite_number)
    else:
        print(f"Bite {bite_number} was not downloaded")


def extract_bite(bite_number):
    """Extracts all the required files into a new directory
    named by the bite number.

    :bite_number: The number of the bite you want to extract.
    :returns: None
    """

    bite = f"pybites_bite{bite_number}.zip"

    try:
        with ZipFile(bite, "r") as zfile:
            zfile.extractall(f"./{bite_number}")

        print(f"Extracted bite {bite_number}")
        os.unlink(bite)

    except FileNotFoundError:
        print("No bite found.")


def submit_bite(bite_number, username, password):
    """Submits bite by pushing to git hub and opening
    webbrowser to the bit page.

    :bite_number: The number of the bite you want to submit.
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

    driver = driver_setup()
    pybites_login(driver, username, password)

    print(f"Locating bite {bite_number} webpage.")
    url = f"https://codechalleng.es/bites/{bite_number}/"
    driver.get(url)
    sleep(1)
    print("Downloading code from GitHub.")
    offline_mode_btn = driver.find_element(By.ID, "githubDropdown")
    offline_mode_btn.click()
    sleep(1)
    github_pull_btn = driver.find_element(By.ID, "ghpull")
    github_pull_btn.click()
    sleep(1)
    print(f"Submitting bite {bite_number}.")
    submit_btn = driver.find_element(By.ID, "save")
    submit_btn.click()
    sleep(1)
    webbrowser.open(url)
