import os

from eatlocal.constants import USERNAME, PASSWORD
from eatlocal.eatlocal import download_bite


def test_eatlocal_downloads_correct_zipfile():
    bite_number = 241
    download_bite(bite_number, USERNAME, PASSWORD)
    assert f"pybites_bite{bite_number}.zip" in os.listdir()
