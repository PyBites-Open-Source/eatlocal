""" eatlocal End to End Tests
"""

from pathlib import Path
from typing import Tuple
from zipfile import is_zipfile

import pytest

from eatlocal.eatlocal import display_bite, download_bite, extract_bite

TEST_BITES = [1, 241, 306]
NOT_DOWNLOADED = [3, 23, 101]


@pytest.mark.slow
@pytest.mark.parametrize(
    "bite_number, creds",
    [
        (241, ("foo", "bar")),
    ],
)
def test_eatlocal_cannot_download_premium_bite_wo_auth(
    bite_number: int,
    creds: Tuple[str, str],
    bites_repo_dir,
    capfd,
) -> None:
    """Attempt to download a bite ZIP archive file with incorrect credentials."""

    download_bite(bite_number, *creds, dest_path=bites_repo_dir, cache_path="cache")
    output = capfd.readouterr()[0]
    assert "was not downloaded" in output


@pytest.mark.slow
@pytest.mark.parametrize("bite_number", TEST_BITES)
def test_eatlocal_downloads_correct_zipfile(
    bite_number: int,
    bites_repo_dir: Path,
    testing_config,
) -> None:
    """Download a ZIP archive file for a specific bite with correct credentials.

    Credentials are obtained either from the environment or the the .env
    located in the directory pytest was launched in.

    Checks for ZIP file existence before and after the download.
    """
    expected = Path(f"cache/pybites_bite{bite_number}.zip").resolve()
    assert not expected.exists()
    download_bite(
        bite_number,
        testing_config["PYBITES_USERNAME"],
        testing_config["PYBITES_PASSWORD"],
        dest_path=bites_repo_dir,
        cache_path="cache",
    )
    assert expected.exists()
    assert is_zipfile(expected)


@pytest.mark.slow
@pytest.mark.parametrize("bite_number", TEST_BITES)
def test_eatlocal_extract_download_zipfile(
    bite_number: int,
    bites_repo_dir: Path,
    testing_config,
) -> None:
    """Download and extract a ZIP archive for a specific bite.

    Checks for bite directory existence before and after the extraction.
    """

    expected = Path(str(bite_number))
    assert not expected.exists()
    extract_bite(
        bite_number,
        dest_path=bites_repo_dir,
        cache_path="cache",
    )
    assert expected.exists()
    assert expected.is_dir()


@pytest.mark.slow
@pytest.mark.parametrize("bite_number", TEST_BITES)
def test_display_bite(
    bite_number: int,
    bites_repo_dir: Path,
    testing_config: dict,
    capfd,
) -> None:
    """Attempt to download a bite ZIP archive file with incorrect credentials."""

    display_bite(bite_number, bite_path=bites_repo_dir, theme="material")
    output = capfd.readouterr()[0]
    assert f"Displaying Bite {bite_number} at" in output
    assert "Code" in output
    assert "Directions" in output


@pytest.mark.parametrize("bite_number", NOT_DOWNLOADED)
def test_cannot_display_missing_bite(
    bite_number: int,
    bites_repo_dir: Path,
    capfd,
) -> None:
    """Attempt to download a bite ZIP archive file with incorrect credentials."""

    display_bite(bite_number, bite_path=bites_repo_dir, theme="material")
    output = capfd.readouterr()[0]
    assert "Unable to display bite" in output
