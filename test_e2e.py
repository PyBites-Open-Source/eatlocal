import psycopg2
import pytest
from decouple import config

from .constants import DOMAIN

bites = []
with psycopg2.connect(dsn=config("DATABASE_URL")) as conn:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT slug, lambda_function, solution FROM bites_bite WHERE published = TRUE"
        )
        bites = cursor.fetchall()


def _slugify(bite):
    slug, lambda_function, _ = bite
    return f"{lambda_function}__{slug}"


@pytest.mark.parametrize("bite", bites, ids=[_slugify(bite) for bite in bites])
def test_bite(logged_in_page, bite):
    slug, _, solution = bite
    page = logged_in_page

    bite_url = f"{DOMAIN}/bites/{slug}/"
    page.goto(bite_url)
    page.wait_for_url(bite_url)

    # page.wait_for_selector("#run-code-button", state="visible")

    page.evaluate(
        f"""document.querySelector('.CodeMirror').CodeMirror.setValue({repr(solution)})"""
    )
    page.click("#validate-button")

    page.wait_for_selector("#feedback", state="visible")

    page.wait_for_function(
        "document.querySelector('#feedback').innerText.includes('Congrats, you passed this Bite')"
    )

    validate_result = page.text_content("#feedback")
    assert "Congrats, you passed this Bite" in validate_result
