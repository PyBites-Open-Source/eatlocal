[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

# eatlocal

Eatlocal helps the user solve [PyBites](https://codechalleng.es) code challenges locally. This cli tool allows you to download, unzip, and organize bites according to the expected structure from PyBites website. You can display bite directions directly in the terminal. Once you have solved the bite you can use eatlocal to submit and it will open a bowser tab at the corresponding bite page.

## Updates

### version 0.8.3

eatlocal is now compatible with Python 3.8. This matches the expected python version for the platform.

### Breaking Changes

+ With version `0.8.0` there is a new `eatlocal init` command. Use this to configure your credentials and local git repository. You no longer need to set environment variables manually.
+ When displaying a bite, there is no longer a live display. The directions and source code are printed to the console. This eliminated the need for the getkey library and made installing eatlocal on windows easier.

## DEMOS

### Configure

![gif of init command](./docs/demos/init.gif)

### Download Bites

![gif of download command](./docs/demos/download.gif) 

### Display Bites

![gif of display command](./docs/demos/display.gif) 

### Submit Bites

![gif of submit command](./docs/demos/submit.gif) 

## Table of Contents

- [eatlocal](#eatlocal)
  - [Updates](#updates)
    - [Version](#version-080)
    - [Breaking Changes](#breaking-changes)
  - [DEMOS](#demos)
    - [Download Bites](#download-bites)
    - [Display Bites](#display-bites)
    - [Submit Bites](#submit-bites)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
  - [Installation](#installation)
    - [macOS/Linux](#macoslinux)
    - [Windows](#windows)
  - [Setup](#setup)
    - [Install Chrome and Chromedriver](#install-chrome-and-chromedriver)
      - [macOS](#macos)
      - [Linux](#linux)
      - [Windows](#windows-1)


## Usage

Set up your configuration file:

```bash
eatlocal init
```

Download and extract bites:

```bash
# use -V, --verbose to print what's happening
eatlocal download <bite number>
```

Display bites in the terminal:

```bash
# change the theme with -t <theme name>
eatlocal display <bite number>
```


Submit bites:

```bash
# use -V, --verbose to print what's happening
eatlocal submit <bite number>

```

## Installation

There are a few options for install eatlocal.

### Using pipx

If you have [pipx](https://pypa.github.io/pipx/) installed:
```bash
pipx install eatlocal
```

### macOS/Linux

```bash
pip3 install eatlocal
```

### Windows

```bash
pip install eatlocal
```

## Setup

1. Go through the directions on the PyBites website to connect your GitHub account to your PyBites account. You will find the necessary steps under `Settings` in the navigation sidebar.
2. Run `eatlocal init` to configure your PyBites username, PyBites password*, and local git repository.
2. Make sure you have Chrome and chromedriver installed and on `$PATH`. The chromedriver version must match the version of your Chrome browser. [Chromedriver downloads](https://chromedriver.chromium.org/downloads).

*Note:  If you signed up for PyBites by authenticating through GitHub or Google, you may need to set a password manually in order to use `eatlocal`.

### Install Chrome and Chromedriver

#### macOS

One option is to use homebrew [homebrew](https://brew.sh/). 

Install chrome:

```bash
brew install --cask google-chrome
```

Install chromedriver:

```bash
brew install chromedriver
```

Before you run chromedriver for the first time (and after you update versions), you must explicitly give permission since the developer has not been verified. Running the following command in the terminal removes the warning put in place by Apple:

```bash
xattr -d com.apple.quarantine $(which chromedriver)
```

Homebrew automatically puts chromedriver on `$PATH` for you. And since homebrew handles both chrome and chromedriver installations for me, I can run `brew update && brew upgrade` to help ensure I have the same version number for both chrome and chromedriver. If you do not go the homebrew route, you must manually ensure that your version of chrome matches the version of chromedriver.


#### Linux

Navigate to the download page for [google chrome](https://www.google.com/chrome/) and download the appropriate version for your system. Then, open up a terminal and navigate to where you downloaded the file. For me it was `~/Downloads`. I ran the following commands to install and check which version I have.

```bash
cd ~/Downloads
sudo dpkg -i google-chrome-stable_current_amd64.deb
google-chrome --version
```

Next, navigate to the [chromedriver download page](https://chromedriver.chromium.org/downloads) and choose the version that matches the output from `google-chrome --version`. Download that file that matches your system. Head back to your terminal.

1. Ensure that you have unzip installed:

```bash
sudo apt install unzip
```

2. Unzip the chromedriver file. For me it was located in the downloads folder: 

```bash
unzip ~/Downloads/chromedriver_linux64.zip -d ~/Downloads
```

3. Make it executable and move to `/usr/local/share`:

```bash
chmod +x ~/Downloads/chromedriver
sudo mv -f ~/Downloads/chromedriver /usr/local/share/chromedriver
```

4. Create symlinks:

```bash
sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
```
5. Confirm you have access:

```bash
which chromedriver
```

#### Windows

If working in windows powershell you can use [chocolately](https://chocolatey.org/) to install both Chrome and chromedriver (with matching versions).

I've found that in order to install packages I have to use an elevated administrative shell, with `choco install chromedriver`.

![chromedriver in chocolatey](https://i.ibb.co/2cCShcd/chromedriver-via-chocolately.png)



##### WSL

`eatlocal` does not work with [WSL2](https://docs.microsoft.com/en-us/windows/wsl/about). There seems to be an issue between [WSL2 and `google-chrome` and chromedriver](https://developercommunity.visualstudio.com/t/selenium-ui-test-can-no-longer-find-chrome-binary/1170486). Perhaps this will be resolved in the future with [WSLg](https://github.com/microsoft/wslg). For now, there is a workaround: Follow instructions for Windows users except install eatlocal globally. Using PowerShell or Windows Terminal, navigate to your WSL distribution's directory that holds your repository and initialize eatlocal from there. Now just download and submit through your external PowerShell command line instead of your bash terminal. Everything should still behave the same, you just can't use your WSL shell or your integrated terminal in VS Code.
