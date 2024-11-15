"""eatlocal unit tests"""

import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

import pytest

from eatlocal.eatlocal import (
    Bite,
    choose_bite,
    choose_local_bite,
    create_bite_dir,
    display_bite,
    get_credentials,
    load_config,
    set_local_dir,
)

NOT_DOWNLOADED = (
    Bite(
        "Made up Bite",
        "made-up-bite",
    ),
    Bite("Write a property", "write-a-property"),
)
LOCAL_TEST_BITE = Bite(
    "Rotate string characters",
    "rotate-string-characters",
)
SUMMING_TEST_BITE = Bite(
    "Sum n numbers",
    "sum-n-numbers",
)


def test_bite_implementation():
    """Test Bite class implementation."""
    bite = SUMMING_TEST_BITE
    assert bite.title == "Sum n numbers"
    assert bite.slug == "sum-n-numbers"
    assert bite.url == "https://pybitesplatform.com/bites/sum-n-numbers/"
    assert bite.platform_content is None


def test_bite_fetch_local_code(testing_config) -> None:
    """Test fetching local code."""
    bite = LOCAL_TEST_BITE
    bite_dir = Path(testing_config["PYBITES_REPO"]) / "rotate-string-characters"
    with open(bite_dir / "rotate.py", "r") as f:
        local_code = f.read()
    bite.fetch_local_code(testing_config)
    assert bite.local_code == local_code


def test_bite_fetch_local_code_no_file(capsys, testing_config) -> None:
    """Test fetching local code when file does not exist."""
    bite = NOT_DOWNLOADED[0]
    bite.fetch_local_code(testing_config)
    output = capsys.readouterr()
    assert "Unable to find bite" in output.out


@patch("eatlocal.eatlocal.iterfzf")
def test_choose_local_bite(mock_iterfzf, testing_config) -> None:
    """Test choosing a local bite."""
    mock_iterfzf.return_value = LOCAL_TEST_BITE.title
    bite = choose_local_bite(testing_config)
    assert bite.title == LOCAL_TEST_BITE.title
    assert bite.slug == LOCAL_TEST_BITE.slug


@patch("eatlocal.eatlocal.Prompt.ask")
@patch("eatlocal.eatlocal.Path.exists")
def test_set_local_dir(mock_exists, mock_prompt):
    mock_prompt.return_value = "/some/path"
    mock_exists.return_value = True
    local_dir = set_local_dir()
    assert local_dir == Path("/some/path")


@patch("eatlocal.eatlocal.requests.get")
@patch("eatlocal.eatlocal.iterfzf")
def test_choose_bite(mock_iterfzf, mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    api_data = json.load(open("./tests/testing_content/bites_api.json"))
    mock_response.json.return_value = api_data
    mock_requests.return_value = mock_response
    mock_iterfzf.return_value = SUMMING_TEST_BITE.title

    bite = choose_bite()
    assert isinstance(bite, Bite)
    assert bite.title == SUMMING_TEST_BITE.title
    assert bite.slug == SUMMING_TEST_BITE.slug


def test_display_bite(
    testing_config,
    capsys,
) -> None:
    """Correctly display a bite that has been downloaded and extracted."""
    display_bite(LOCAL_TEST_BITE, testing_config, theme="material")
    output = capsys.readouterr().out
    assert f"Displaying {LOCAL_TEST_BITE.title} at" in output
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
    with open(Path("./tests/testing_content/summing_content.txt"), "r") as f:
        platform_content = f.read()
    bite = SUMMING_TEST_BITE
    bite.platform_content = platform_content
    bite_dir = Path(testing_config["PYBITES_REPO"]) / "sum-n-numbers"

    create_bite_dir(bite, testing_config)
    html_file = bite_dir / "bite.html"
    python_file = bite_dir / "summing.py"
    test_file = bite_dir / "test_summing.py"
    assert html_file.exists()
    assert python_file.exists()
    assert test_file.exists()
    assert bite_dir.is_dir()
    assert bite_dir.name == "sum-n-numbers"
    shutil.rmtree(bite_dir)


def test_create_bite_dir_without_force(testing_config, capsys):
    create_bite_dir(LOCAL_TEST_BITE, testing_config)
    output = capsys.readouterr().out
    assert "There already exists a directory for" in output
    assert "Use the --force option" in output


def test_load_config() -> None:
    """Load the configuration file."""
    expected = {
        "PYBITES_USERNAME": "test_username",
        "PYBITES_PASSWORD": "test_password",
        "PYBITES_REPO": "test_repo",
    }
    actual = load_config(Path("./tests/testing_content/testing_env").resolve())
    assert actual == expected


def test_load_config_file_not_found(capsys) -> None:
    """Test loading a config file that does not exist."""
    with pytest.raises(SystemExit):
        load_config(Path("./tests/testing_content/non_existent_file").resolve())
    output = capsys.readouterr().out
    assert "Could not find or read .eatlocal/.env in your home directory." in output


@patch("eatlocal.eatlocal.Prompt.ask")
def test_get_credentials(mock_prompt) -> None:
    """Test getting credentials from the config file."""
    expected = ("test_username", "test_password")
    mock_prompt.side_effect = ["test_username", "test_password", "test_password"]
    actual = get_credentials()
    assert actual == expected
