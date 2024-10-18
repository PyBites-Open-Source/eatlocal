""" eatlocal End to End Tests
"""

from pathlib import Path
from zipfile import is_zipfile

import pytest

from eatlocal.__main__ import download

TEST_BITES = [1, 243, 325]


@pytest.mark.slow
@pytest.mark.parametrize(
    "bite_number, creds",
    [
        (241, ("foo", "bar")),
    ],
)
def test_eatlocal_cannot_download_premium_bite_wo_auth(
    bite: int,
    creds: tuple[str, str],
    bites_repo_dir,
    capfd,
) -> None:
    """Attempt to download a bite ZIP archive file with incorrect credentials."""

    create_bite_dir(bite_number, *creds, dest_path=bites_repo_dir, cache_path="cache")
    output = capfd.readouterr()[0]
    assert "was not downloaded" in output
