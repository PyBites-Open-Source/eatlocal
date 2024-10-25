"""eatlocal unit tests"""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from eatlocal.eatlocal import (
    Bite,
    choose_bite,
    choose_local_bite,
    create_bite_dir,
    display_bite,
    load_config,
    set_repo,
)

NOT_DOWNLOADED = (
    Bite(
        "Made up Bite",
        "https://pybitesplatform.com/bites/made-up-bite/",
    ),
    Bite("Write a property", "https://pybitesplatform.com/bites/write-a-property/"),
)
LOCAL_TEST_BITE = Bite(
    "Rotate string characters",
    "https://pybitesplatform.com/bites/rotate-string-characters/",
)


def test_bite_implementation():
    """Test Bite class implementation."""
    bite = Bite("Sum n Numbers", "https://pybitesplatform.com/bites/sum-n-numbers/")
    assert bite.title == "Sum n Numbers"
    assert bite.url == "https://pybitesplatform.com/bites/sum-n-numbers/"
    assert bite.platform_content is None


def test_bite_fetch_local_code(testing_config) -> None:
    """Test fetching local code."""
    bite = Bite(
        "Rotate string characters",
        "https://pybitesplatform.com/bites/rotate-string-characters/",
    )
    bite_dir = Path(testing_config["PYBITES_REPO"]) / "rotate_string_characters"
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
    assert bite[0] == LOCAL_TEST_BITE.title
    assert bite[1] == LOCAL_TEST_BITE.url


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
    with open("./tests/testing_content/summing_content.txt", "r") as f:
        platform_content = f.read()
    bite = Bite("Sum n Numbers", "https://pybitesplatform.com/bites/sum-n-numbers/")
    bite.platform_content = platform_content
    bite_dir = Path(testing_config["PYBITES_REPO"]) / "sum_n_numbers"

    create_bite_dir(bite, testing_config)
    html_file = bite_dir / "bite.html"
    python_file = bite_dir / "summing.py"
    test_file = bite_dir / "test_summing.py"
    assert html_file.exists()
    assert python_file.exists()
    assert test_file.exists()
    assert bite_dir.is_dir()
    assert bite_dir.name == "sum_n_numbers"
    shutil.rmtree(bite_dir)


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
