from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from zipfile import ZipFile
import subprocess
import webbrowser


def download_bite(bite_number, username, password):
    """Download bite .zip from the platform.

    :bite_number: The number of the bite you want to download.
    :returns: None
    """

    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1920x1080")
    driver = webdriver.Chrome(options=options)

    login_url = "https://codechalleng.es/login"

    print("Logging into PyBites")
    driver.get(login_url)
    username_field = driver.find_element(By.ID, "id_username")
    username_field.send_keys(username)
    password_field = driver.find_element(By.ID, "id_password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    print(f"Retrieving bite {bite_number}")
    sleep(2)
    bite_url = f"https://codechalleng.es/bites/api/downloads/bites/{bite_number}"
    driver.get(bite_url)
    sleep(2)
    print(f"Bite {bite_number} successully downloaded to current directory")
    extract_bite(bite_number)


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
        subprocess.call(["rm", bite])

    except FileNotFoundError:
        print("No bite found.")


def submit_bite(bite_number):
    """Submits bite by pushing to git hub and opening
    webbrowser to the bit page.

    :bite_number: The number of the bite you want to submit.
    :returns: None
    """

    subprocess.call(
        ["git", "add", "."],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    subprocess.call(
        ["git", "commit", f"-m'submission Bite {bite_number} @ codechalleng.es'"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    subprocess.call(
        ["git", "push"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    print(f"\nPushed bite {bite_number} to github")

    url = f"https://codechalleng.es/bites/{bite_number}/"
    webbrowser.open(url)
