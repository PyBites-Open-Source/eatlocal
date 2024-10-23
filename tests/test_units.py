"""eatlocal unit tests"""

from pathlib import Path
from unittest import mock

import pytest

from eatlocal.eatlocal import display_bite, submit_bite, Bite, create_bite_dir

NOT_DOWNLOADED = (
    Bite(
        "Parsing a list of names",
        "https://pybitesplatform.com/bites/parse-a-list-of-names/",
    ),
    Bite("Write a property", "https://pybitesplatform.com/bites/write-a-property/"),
)
LOCAL_TEST_BITES = (
    Bite("Sum n Numbers", "https://pybitesplatform.com/bites/sum-n-numbers/"),
)

TESTING_REPO = Path("./tests/testing_repo/").resolve()

@pytest.mark.parametrize("bite", LOCAL_TEST_BITES)
def test_display_bite(
    bite,
    testing_config,
    capsys,
) -> None:
    """Correctly display a bite that has been downloaded and extracted."""
    testing_config["PYBITES_REPO"] = Path("./tests/testing_content/")
    display_bite(bite, testing_config, theme="material")
    output = capsys.readouterr().out
    assert f"Displaying {bite.title} at" in output
    assert "Code" in output
    assert "Directions" in output


@pytest.mark.parametrize("bite", NOT_DOWNLOADED)
def test_cannot_display_missing_bite(
    bite,
    testing_config,
    capsys,
) -> None:
    """Attempt to display a bite that has not been downloaded and extracted."""

    display_bite(bite, testing_config, theme="material")
    output = capsys.readouterr().out
    assert "Unable to display bite" in output


def test_create_bite_dir(
    testing_config,
    tmp_path,
) -> None:
    """Create a directory for a bite."""
    with open("./tests/testing_content/summing_content.txt", "r") as f:
        platform_content = f.read()
    bite = Bite("Sum n Numbers", "https://pybitesplatform.com/bites/sum-n-numbers/")
    bite.platform_content = platform_content
    bite_dir = tmp_path / "sum_n_numbers"
    create_bite_dir(bite, testing_config, tmp_path)
    assert bite_dir.exists()
    assert bite_dir.is_dir()
    assert bite_dir.name == "sum_n_numbers"
