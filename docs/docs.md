# eatlocal

Eatlocal helps the user solve [Pybites](https://codechallang.es) code challenges locally. The cli tool allows you to download, unzip, and organize bites according to the expected structure from the directions on the PyBites website. Once you have solved the bite you can use eatlocal to submit and it will open a bowser tab at the correct location.

## Table of Contents

+ [Usage](#Usage)
+ [Installation](#Installation)
+ [Setup](#Setup)
	+ [Chrome and Chromedriver](#Chrome-and-Chromedriver)
		+ [macOS](#macOS)
		+ [Windows](#Windows)
		+ [Linux](#Linux)
			+ [Install Chrome](#Install-Chrome)
			+ [Install chromedriver](#Install-chromedriver)
	+ [PyBites Credentials](#PyBites-Credentials)
		+ [macOS/Linux](#macOS/Linux)
		+ [Windows](#Windows)


## Usage

Navigate to your local PyBites repo.

Download and extract bites with the --download flag: `eatlocal -d <bite number>`

Unzip and organize bites that have been already downloaded with the --extract flag: `eatlocal -e <bite number>`

Submit bites with the --submit flag: `eatlocal -s <bite number>`


## Installation

`pip install eatlocal`

## Setup

1. Go through the directions on the PyBites website to connect your GitHub account to your PyBites account.
2. Make sure you have Chrome and chromedriver installed and on `$PATH`.
3. Setup your PyBites login credentials as environment variables. If you signed up for PyBites by authenticating through GitHub or Google, you may need to set a password manually in order to use eatlocal.

### Chrome and Chromedriver

#### macOS

Install chrome and chromedriver with with [homebrew](https://brew.sh/). 

Install chrome:

`brew install --cask google-chrome`

Install chromedriver:

`brew install chromedriver`

Before you run chromedriver for the first time, you must explicitly give permission since the developer has not been verified. Running the following command in the terminal removes the warning put in place by Apple:

`xattr -d com.apple.quarantine $(which chromedriver)`

Homebrew automatically puts chromedriver on `$PATH` for you. And since homebrew handles both chrome and chromedriver installations for me, I can run `brew update && brew upgrade` to help ensure I have the same version number for both chrome and chromedriver. If you do not go the homebrew route, you must manually ensure that your version of chrome matches the version of chromedriver.

#### Windows

If working in windows powershell you can use [chocolately](https://chocolatey.org/) to install chromedriver. I've found that in order to install packages I have to use an elevated administrative shell, with `choco install chromedriver`. I attempted to use `eatlocal` from [WSL2](https://docs.microsoft.com/en-us/windows/wsl/about) but there seems to be an issue with `google-chrome` itself. I could not get it to work.

#### Linux

Unfortunately, I did not find some fancy package manager for Linux, but I was able to install chrome and chromedriver manually for Linux Mint.

##### Install Chrome

Navigate to the download page for [google chrome](https://www.google.com/chrome/) and download the appropriate version for your system. Then, open up a terminal and navigate to where you downloaded the file. For me it was `~/Downloads`. I ran the following commands to install and check which version I have.

```bash
cd ~/Downloads
sudo dpkg -i google-chrome-stable_current_amd64.deb
google-chrome --version
```

##### Install chromedriver

Navigate to the chromedriver download page and choose the version that matches the output from `google-chrome --version`. Download that file that matches your system. Head back to your terminal.
1. Ensure that you have unzip installed: `sudo apt install unzip`
2. Unzip the chromedriver file. For me it was located in the downloads folder: `unzip ~/Downloads/chromedriver_linux64.zip -d ~/Downloads`
3. Make it executable and move to `/usr/local/share`:
```bash
chmod +x ~/Downloads/chromedriver
sudo mv -f ~/Downloads/chromedriver /usr/local/share/chromedriver
```
4. Create symlinks: `sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver`
5. Confirm you have access: `which chromedriver`

### PyBites Credentials

You must have your PyBites username and password stored in the environment variables `PYBITES_USERNAME` and `PYBITES_PASSWORD` respectively.

#### macOS/Linux

There are two methods to handle this in.

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
2. Either exit close your terminal completely and reopen, or source your config file with `source ~/.zshrc`.

#### Windows

I don't know of a way to do this other than graphically (Booo!). If you want pictures you can follow this [tutorial](https://windowsloop.com/add-environment-variable-in-windows-10).

1. Open the Start menu by pressing the “Windows Key”.
2. Type “Environment variables” and click on the “Edit the system environment variables” result.
3. Click on the "Advanced" tab.
4. Click "Environment Variables".
5. Under "User variables" click "New".
6. In the "Variable name" field enter: PYBITES_USERNAME
7. In the "Variable value" field enter: <username>
8. Repeat for the password variable.
9. Click "Ok"
10. Click "Apply"
11. Restart your computer.
