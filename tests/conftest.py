"""eatlocal specific pytest configuration

"""


import os
import shutil

from pathlib import Path
from typing import Union, Generator

import pytest


@pytest.fixture
def bites_repo_dir(tmp_path) -> Generator[Path, None, None]:

    cwd = Path.cwd()

    os.chdir(tmp_path)

    yield tmp_path

    os.chdir(cwd)
