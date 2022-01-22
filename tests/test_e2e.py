import os
import shutil

import pytest

from eatlocal.constants import USERNAME, PASSWORD
from eatlocal.eatlocal import download_bite


def test_eatlocal_cannot_download_premium_bite_wo_auth(capfd):
    bite_number = 241
    download_bite(bite_number, "foo", "bar")
    output = capfd.readouterr()[0]
    assert "Bite 241 was not downloaded" in output


@pytest.mark.parametrize("bite_number", [1, 241, 306])
def test_eatlocal_downloads_correct_zipfile(bite_number):
    download_bite(bite_number, USERNAME, PASSWORD)
    bite_dir = str(bite_number)
    assert os.path.isdir(bite_dir)
    shutil.rmtree(bite_dir)
