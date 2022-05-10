"""eatlocal unit tests"""

from pathlib import Path
from shutil import rmtree

import pytest

from eatlocal.eatlocal import display_bite, extract_bite, submit_bite

TESTING_REPO = Path("./tests/testing_repo/").resolve()
NOT_DOWNLOADED = (426, 499)
LOCAL_TEST_ZIPS = (101, 102)
LOCAL_TEST_BITES = (103, 104)


@pytest.mark.parametrize("bite_number", LOCAL_TEST_ZIPS)
def test_extract_zipfile(
    bite_number: int,
) -> None:
    """Extract a ZIP archive for a specific bite.
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
def test_cannot_extract_existing_bite(
    bite_number: int,
    capsys,
) -> None:
    """Checks that an existing bite can not be extracted unless forced."""

    extract_bite(
        bite_number,
        dest_path=TESTING_REPO,
        cache_path="cache",
    )
    output = capsys.readouterr().out
    assert f"There already exists a directory for bite {bite_number}. " in output


@pytest.mark.parametrize("bite_number", NOT_DOWNLOADED)
def test_cannot_extract_missing_bite(
    bite_number: int,
    capsys,
) -> None:
    """Checks that an existing bite can not be extracted unless forced."""

    extract_bite(
        bite_number,
        dest_path=TESTING_REPO,
        cache_path="cache",
    )
    output = capsys.readouterr().out
    assert f"Missing ZIP archive for bite {bite_number}" in output


@pytest.mark.parametrize("bite_number", LOCAL_TEST_BITES)
def test_display_bite(
    bite_number: int,
    capsys,
) -> None:
    """Correctly display a bite that has been downloaded and extracted."""

    display_bite(bite_number, bite_repo=TESTING_REPO, theme="material")
    output = capsys.readouterr().out
    assert f"Displaying Bite {bite_number} at" in output
    assert "Code" in output
    assert "Directions" in output


@pytest.mark.parametrize("bite_number", NOT_DOWNLOADED)
def test_cannot_display_missing_bite(
    bite_number: int,
    capsys,
) -> None:
    """Attempt to display a bite that has not been downloaded and extracted."""

    display_bite(bite_number, bite_repo=TESTING_REPO, theme="material")
    output = capsys.readouterr().out
    assert "Unable to display bite" in output


@pytest.mark.parametrize("bite_number", LOCAL_TEST_BITES)
def test_submit_from_nongit_repo(
    bite_number: int,
    testing_config,
    capsys,
) -> None:
    """Attempt to submit from an invalid git repository."""

    submit_bite(
        bite_number,
        testing_config["PYBITES_USERNAME"],
        testing_config["PYBITES_PASSWORD"],
        TESTING_REPO,
    )
    output = capsys.readouterr().out
    assert "Not a valid git repo:" in output


@pytest.mark.parametrize("bite_number", NOT_DOWNLOADED)
def test_submit_missing_bite(
    bite_number: int,
    testing_config,
    capsys,
) -> None:
    """Attempt to submit from an invalid git repository."""
    submit_bite(
        NOT_DOWNLOADED,
        testing_config["PYBITES_USERNAME"],
        testing_config["PYBITES_PASSWORD"],
        testing_config["PYBITES_REPO"],
    )
    output = capsys.readouterr().out
    assert "Did you mean" in output
