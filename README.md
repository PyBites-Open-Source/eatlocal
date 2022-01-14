# eatlocal

This package helps the user solve [Pybites](https://codechallang.es) locally.

## Usage

Go through the directions on the Pybites website to connect your GitHub account to your PyBites account.

Note: in order for the download flag to work properly, you must have your username and password stored in environment variables `PYBITES_USERNAME` and `PYBITES_PASSWORD` respectively. You also need to have chromedriver installed and on $PATH. Since I use macos, I handled with with homebrew: `brew install chromedriver`.

Extract bites you have already downloaded with the --extract flag:
`eatlocal -e <bite number>`

Download bites with the --download flag:
`eatlocal -d <bite number>`

Submit bites with the --submit flag:
`eatlocal -s <bite number>`
