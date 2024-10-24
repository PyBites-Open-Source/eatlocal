"""eatlocal unit tests"""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from eatlocal.eatlocal import (
    Bite,
    choose_bite,
    create_bite_dir,
    display_bite,
    download_bite,
    set_repo,
    submit_bite,
)

NOT_DOWNLOADED = (
    Bite(
        "Parsing a list of names",
        "https://pybitesplatform.com/bites/parse-a-list-of-names/",
    ),
    Bite("Write a property", "https://pybitesplatform.com/bites/write-a-property/"),
)
LOCAL_TEST_BITES = (
    Bite(
        "Rotate string characters",
        "https://pybitesplatform.com/bites/rotate-string-characters/",
    ),
)


@patch("eatlocal.eatlocal.Prompt.ask")
@patch("eatlocal.eatlocal.Path.exists")
def test_set_repo(mock_exists, mock_prompt):
    mock_prompt.return_value = "/some/path"
    mock_exists.return_value = True
    repo = set_repo()
    assert repo == Path("/some/path")
    mock_exists.assert_called_once()


@patch("eatlocal.eatlocal.requests.get")
@patch("eatlocal.eatlocal.iterfzf")
def test_choose_bite(mock_iterfzf, mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    with open("./tests/testing_content/bites_list.html") as f:
        mock_response.content = f.read()
    mock_requests.return_value = mock_response
    mock_iterfzf.return_value = "Sum n numbers"

    bite_name, bite_url = choose_bite()
    assert bite_name == "Sum n numbers"
    assert bite_url == "https://pybitesplatform.com/bites/sum-n-numbers/"


@pytest.mark.parametrize("bite", LOCAL_TEST_BITES)
def test_display_bite(
    bite,
    testing_config,
    capsys,
) -> None:
    """Correctly display a bite that has been downloaded and extracted."""
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
) -> None:
    """Create a directory for a bite."""
    with open("./tests/testing_content/summing_content.txt", "r") as f:
        platform_content = f.read()
    bite = Bite("Sum n Numbers", "https://pybitesplatform.com/bites/sum-n-numbers/")
    bite.platform_content = platform_content
    bite_dir = Path(testing_config["PYBITES_REPO"]) / "sum_n_numbers"
    create_bite_dir(bite, testing_config)
    assert bite_dir.exists()
    assert bite_dir.is_dir()
    assert bite_dir.name == "sum_n_numbers"
    shutil.rmtree(bite_dir)
