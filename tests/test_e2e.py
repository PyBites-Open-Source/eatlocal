""" eatlocal End to End Tests
"""

from pathlib import Path
from typing import Tuple
from zipfile import is_zipfile

import pytest

from eatlocal.constants import USERNAME, PASSWORD
from eatlocal.eatlocal import download_bite, extract_bite

TEST_BITES = [1, 241, 306]


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
    capfd,
) -> None:
    """Attempt to download a bite ZIP archive file with incorrect credentials."""

    download_bite(bite_number, *creds)
    output = capfd.readouterr()[0]
    assert "was not downloaded" in output


@pytest.mark.slow
@pytest.mark.parametrize("bite_number", TEST_BITES)
def test_eatlocal_downloads_correct_zipfile(
    bite_number: int,
    bites_repo_dir: Path,
) -> None:
    """Download a ZIP archive file for a specific bite with correct credentials.

    Credentials are obtained either from the environment or the the .env
    located in the directory pytest was launched in.

    Checks for ZIP file existence before and after the download.
    """
    expected = Path(f"pybites_bite{bite_number}.zip")
    assert not expected.exists()
    download_bite(bite_number, USERNAME, PASSWORD)
    assert expected.exists()
    assert is_zipfile(expected)


@pytest.mark.slow
@pytest.mark.parametrize("bite_number", TEST_BITES)
def test_eatlocal_extract_download_zipfile(
    bite_number: int,
    bites_repo_dir: Path,
) -> None:
    """Download and extract a ZIP archive for a specific bite.

    Checks for bite directory existence before and after the extraction.
    """

    expected = Path(str(bite_number))
    download_bite(bite_number, USERNAME, PASSWORD)
    assert not expected.exists()
    extract_bite(bite_number)
    assert expected.exists()
    assert expected.is_dir()
