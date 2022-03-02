from pathlib import Path
from typing import Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .constants import LOGIN_URL


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


def pybites_login(
    driver: webdriver.Chrome, username: str, password: str, verbose: bool = False
) -> None:
    """Authenticate this driver instance with the given credentials.

    :driver: webdriver.Chrome
    :username: str
    :password: str
    :returns: None
    """

    if verbose:
        print("Logging into PyBites")
    driver.get(LOGIN_URL)

    username_field = driver.find_element(By.ID, "id_username")
    username_field.send_keys(username)
    password_field = driver.find_element(By.ID, "id_password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
