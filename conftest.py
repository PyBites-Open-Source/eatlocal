import pytest
from playwright.sync_api import sync_playwright

from .constants import LOGIN, PASSWORD, DOMAIN, HEADLESS


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        with p.chromium.launch(headless=HEADLESS) as browser:
            yield browser


@pytest.fixture(scope="session")
def logged_in_page(browser):
    page = browser.new_page()
    # only shorten for debugging, some bites need in e2e test need longer
    page.set_default_timeout(30000)
    page.goto(DOMAIN)

    page.click("#login-link")
    page.fill('input[name="login"]', LOGIN)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')

    yield page
