"""eatlocal specific pytest configuration
"""


import os
from pathlib import Path
from typing import Generator

import pytest
from dotenv import dotenv_values

from eatlocal.constants import EATLOCAL_HOME


@pytest.fixture
def bites_repo_dir(tmp_path) -> Generator[Path, None, None]:
    cwd = Path.cwd()
    os.chdir(tmp_path)

    yield tmp_path

    os.chdir(cwd)


@pytest.fixture
def testing_config() -> dict:
    config = {"PYBITES_USERNAME": "", "PYBITES_PASSWORD": "", "PYBITES_REPO": ""}
    config.update(dotenv_values(dotenv_path=Path(EATLOCAL_HOME / ".env")))
    return config
