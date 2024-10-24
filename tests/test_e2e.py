"""eatlocal End to End Tests"""


from typer.testing import CliRunner
from eatlocal.eatlocal import download_bite, Bite
from eatlocal.__main__ import cli, EATLOCAL_HOME
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

runner = CliRunner()

TEST_BITE = Bite("Sum n Numbers", "sum-n-numbers")
TEST_BITES = []
BAD_CONFIG = {
    "PYBITES_USERNAME": "foo",
    "PYBITES_PASSWORD": "bar",
    "PYBITES_REPO": "baz",
}


def test_eatlocal_cannot_download_premium_bite_wo_auth(
    capfd,
) -> None:
    """Test that a premium bite cannot be downloaded without credentials."""

    download_bite(TEST_BITE, BAD_CONFIG, verbose=True)
    output = capfd.readouterr()[0]
    assert "Unable to login to PyBites." in output


@patch("builtins.open", new_callable=mock_open)
@patch("eatlocal.__main__.EATLOCAL_HOME", new=MagicMock())
@patch("eatlocal.__main__.get_credentials")
@patch("eatlocal.__main__.set_repo")
@patch("eatlocal.__main__.Confirm.ask")
@patch("eatlocal.__main__.install_browser")
def test_init_command(
    mock_install_browser,
    mock_confirm_ask,
    mock_set_repo,
    mock_get_credentials,
    mock_open,
):
    mock_get_credentials.return_value = ("test_user", "test_password")
    mock_set_repo.return_value = Path("/mock/repo")
    mock_confirm_ask.return_value = True
    # EATLOCAL_HOME.is_dir.return_value = True

    result = runner.invoke(cli, ["init", "--verbose"])
    assert Path(EATLOCAL_HOME).is_dir()

    assert result.exit_code == 0
    assert "Successfully stored configuration variables" in result.output

    mock_install_browser.assert_called_once_with(True)
