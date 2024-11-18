"""eatlocal End to End Tests"""

from typer.testing import CliRunner
from eatlocal.eatlocal import download_bite, Bite
from eatlocal.__main__ import cli, EATLOCAL_HOME
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import shutil

import pytest

runner = CliRunner()

SUMMING_TEST_BITE = Bite(
    "Sum n Numbers",
    "sum-n-numbers",
)
TEST_BITES = []
BAD_CONFIG = {
    "PYBITES_USERNAME": "foo",
    "PYBITES_PASSWORD": "bar",
    "PYBITES_REPO": "baz",
}
TEST_DOWNLOAD_BITE = "parse-a-list-of-names"


@pytest.mark.slow
def test_eatlocal_cannot_download_premium_bite_wo_auth(
    capfd,
) -> None:
    """Test that a premium bite cannot be downloaded without credentials."""
    with pytest.raises(SystemExit):
        download_bite(SUMMING_TEST_BITE, BAD_CONFIG)
        output = capfd.readouterr()[0]
        assert "Unable to login to PyBites." in output


@patch("builtins.open", new_callable=mock_open)
@patch("eatlocal.eatlocal.EATLOCAL_HOME", new=MagicMock())
@patch("eatlocal.eatlocal.LOCAL_BITES_DB", new=MagicMock())
@patch("eatlocal.eatlocal.get_credentials")
@patch("eatlocal.eatlocal.set_local_dir")
@patch("eatlocal.eatlocal.Confirm.ask")
@patch("eatlocal.eatlocal.install_browser")
def test_init_command(
    mock_install_browser,
    mock_confirm_ask,
    mock_set_local_dir,
    mock_get_credentials,
    mock_open,
):
    """Test the init command."""
    mock_get_credentials.return_value = ("test_user", "test_password")
    mock_set_local_dir.return_value = Path("/mock/local_dir")
    mock_confirm_ask.return_value = True

    runner.invoke(cli, ["init"])
    assert Path(EATLOCAL_HOME).is_dir()


@pytest.mark.slow
@patch("eatlocal.__main__.load_config")
@patch("eatlocal.eatlocal.iterfzf")
def test_download_command(mock_iterfzf, mock_load_config, testing_config):
    """Test the download command."""
    mock_load_config.return_value = testing_config
    mock_iterfzf.return_value = "Parse a list of names"

    runner.invoke(cli, ["download"])

    assert (
        (Path(testing_config["PYBITES_REPO"]) / TEST_DOWNLOAD_BITE).resolve().is_dir()
    )

    shutil.rmtree(Path(testing_config["PYBITES_REPO"]) / TEST_DOWNLOAD_BITE)


@pytest.mark.slow
@patch("eatlocal.__main__.load_config")
@patch("eatlocal.eatlocal.iterfzf")
def test_submit_command(mock_iterfzf, mock_load_config, testing_config):
    """Test the submit command."""
    mock_load_config.return_value = testing_config
    mock_iterfzf.return_value = "Rotate string characters"
    result = runner.invoke(cli, ["submit"])

    assert "Code did not pass the tests." in result.output
