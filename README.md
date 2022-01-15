# eatlocal

This package helps the user solve [Pybites](https://codechallang.es) code challenges locally.

## Usage

Go through the directions on the PyBites website to connect your GitHub account to your PyBites account. eatlocal allows you to download bites, unzip, and organize them according to the expected structure from the directions on the PyBites website. Once you have solved the bite you can submit it and the eatlocal will open a bowser tab at the correct location.

Download and extract bites with the --download flag: `eatlocal -d <bite number>`

Unzip and organize bites you have already downloaded with the --extract flag: `eatlocal -e <bite number>`

Submit bites with the --submit flag: `eatlocal -s <bite number>`

## Requirements

In order for the download flag to work properly, you must have chromedriver on $PATH. Since I use macOS, I handled this with [homebrew](https://brew.sh/): `brew install chromedriver`. Homebrew automatically puts chromedriver on path for you. You must also have your PyBites username and password stored in the environment variables `PYBITES_USERNAME` and `PYBITES_PASSWORD` respectively. There are two methods to handle this. 

### Virtual Environment Method

1. Create a virtual environment for your pybites repo:
	- `python3 -m venv .venv`
2. With the environment deactivated, use your favorite text editor to open the activate file, e.g. `nvim .venv/bin/activate` and add the following lines:
	- `export PYBITES_USERNAME=<username>`
	- `export PYBITES_PASSWORD=<password>`
3. Activate the environment `source .venv/bin/activate`.

### Shell RC Method

1. If you are not using a virtual environment, you can add the variables directly to your shell config. I use zsh, so I would use my favorite text editor `nvim ~/.zshrc` and set the variables by adding the same two lines as above:
	- `export PYBITES_USERNAME=<username>`
	- `export PYBITES_PASSWORD=<password>`
2. Either exit close your shell completely and reopen, or source your config file with `source ~/.zshrc`.
