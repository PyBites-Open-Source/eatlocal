
from pathlib import Path
from shutil import rmtree

import pytest

from eatlocal.eatlocal import display_bite, extract_bite

TESTING_REPO = Path("./tests/testing_repo/").resolve()
NOT_DOWNLOADED = (3, 23)
LOCAL_TEST_ZIPS = (5, 30)
LOCAL_TEST_BITES = (2, 241)


@pytest.mark.parametrize("bite_number", LOCAL_TEST_ZIPS)
def test_extract_zipfile(
    bite_number: int,
) -> None:
    """Download and extract a ZIP archive for a specific bite.

    Checks for bite directory existence before and after the extraction.
    """

    expected = Path(TESTING_REPO / str(bite_number)).resolve()
    assert not expected.exists()
    extract_bite(
        bite_number,
        dest_path=TESTING_REPO,
        cache_path="cache",
    )
    assert expected.exists()
    assert expected.is_dir()
    rmtree(expected)


@pytest.mark.parametrize("bite_number", LOCAL_TEST_BITES)
def test_display_bite(
    bite_number: int,
    capfd,
) -> None:
    """Attempt to download a bite ZIP archive file with incorrect credentials."""

    display_bite(bite_number, bite_path=TESTING_REPO, theme="material")
    output = capfd.readouterr()[0]
    assert f"Displaying Bite {bite_number} at" in output
    assert "Code" in output
    assert "Directions" in output


@pytest.mark.parametrize("bite_number", NOT_DOWNLOADED)
def test_cannot_display_missing_bite(
    bite_number: int,
    capfd,
) -> None:
    """Attempt to download a bite ZIP archive file with incorrect credentials."""

    display_bite(bite_number, bite_path=TESTING_REPO, theme="material")
    output = capfd.readouterr()[0]
    assert "Unable to display bite" in output
