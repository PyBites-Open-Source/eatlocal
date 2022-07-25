from typer.testing import CliRunner

from eatlocal.__main__ import cli

runner = CliRunner()


def test_version():
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.8.3" in result.stdout
