"""eatlocal End to End Tests"""


from eatlocal.eatlocal import download_bite, Bite

TEST_BITE = Bite("Sum n Numbers", "sum-n-numbers")
TEST_BITES = []
BAD_CONFIG = {"PYBITES_USERNAME": "foo", "PYBITES_PASSWORD": "bar", "PYBITES_REPO": "baz"}


def test_eatlocal_cannot_download_premium_bite_wo_auth(
    capfd,
) -> None:
    """Test that a premium bite cannot be downloaded without credentials."""

    download_bite(TEST_BITE, BAD_CONFIG, verbose=True)
    output = capfd.readouterr()[0]
    assert "Unable to login to PyBites." in output
