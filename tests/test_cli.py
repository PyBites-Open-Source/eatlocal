from typer.testing import CliRunner

from eatlocal.__main__ import cli
from eatlocal.__init__ import __version__

runner = CliRunner()


def test_version():
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
