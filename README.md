# eatlocal

This package helps the user solve [Pybites](https://codechallang.es) code challenges locally.

## Usage

Eatlocal allows you to download bites, unzip, and organize them according to the expected structure from the directions on the PyBites website. Once you have solved the bite you can submit it and the eatlocal will open a bowser tab at the correct location.

Navigate to your local PyBites repo.

Download and extract bites with the --download flag: `eatlocal -d <bite number>`

Unzip and organize bites that have been already downloaded with the --extract flag: `eatlocal -e <bite number>`

Submit bites with the --submit flag: `eatlocal -s <bite number>`


## Installation

`pip install eatlocal`

## Setup

1. Go through the directions on the PyBites website to connect your GitHub account to your PyBites account.
2. Make sure you have Chrome and chromedriver installed and on `$PATH`.
3. Setup your PyBites login credentials as environment variables.

### Chrome and Chromedriver

#### macOS

I handle this with [homebrew](https://brew.sh/). 
- Install chrome: `brew install --cask google-chrome`
- Install chromedriver: `brew install chromedriver`
- Before you run chromedriver for the first time, you must explicitly give permission since the developer has not been verified. Running the following command in your shell removes the warning put in place by Apple: `xattr -d com.apple.quarantine $(which chromedriver)`

Homebrew automatically puts chromedriver on `$PATH` for you. And since homebrew handles both chrome and chromedriver installations for me, I can run `brew update && brew upgrade` to help ensure I have the same version number for both chrome and chromedriver. If you do not go the homebrew route, you must manually ensure that your version of chrome matches the version of chromedriver.

#### Windows

If working in windows powershell you can use [chocolately](https://chocolatey.org/) to install chromedriver. I've found that in order to install packages I have to use an elevated administrative shell, with `choco install chromedriver`. I attempted to use `eatlocal` from [WSL2](https://docs.microsoft.com/en-us/windows/wsl/about) but there seems to be an issue with `google-chrome` itself. I could not get it to work.

#### Linux

I have not tried it yet.

### PyBites Credentials

You must have your PyBites username and password stored in the environment variables `PYBITES_USERNAME` and `PYBITES_PASSWORD` respectively.

#### macOS/Linux
There are two methods to handle this in unix/linux (I have not tested in linux yet).

**Virtual Environment Method**

A note of warning. If you use this method make sure that your virtual environment is not being pushed to GitHub. If you have pushed your virtual environment you exposed your password and should change it immediately.

1. Create a virtual environment for your PyBites repo:
	- `python3 -m venv .venv`
2. Add the line `.venv` to your `.gitignore` file.
3. With the environment deactivated, use your favorite text editor to open the activate file, e.g., `nvim .venv/bin/activate` and add the following lines:
	- `export PYBITES_USERNAME=<username>`
	- `export PYBITES_PASSWORD=<password>`
4. Activate the environment `source .venv/bin/activate`.

**Shell RC Method**

If you are not using a virtual environment, you can add the variables directly to your shell config. 

1. I use zsh, so I would use my favorite text editor `nvim ~/.zshrc` and set the variables by adding the same two lines as above:
	- `export PYBITES_USERNAME=<username>`
	- `export PYBITES_PASSWORD=<password>`
2. Either exit close your shell completely and reopen, or source your config file with `source ~/.zshrc`.
