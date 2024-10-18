[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

# eatlocal

Eatlocal helps the user solve [PyBites](https://codechalleng.es) code challenges locally. This cli tool allows you to download bites from the new platform. You can display bite directions directly in the terminal. Once you have solved the bite you can use eatlocal to submit and it will open a bowser tab at the corresponding bite page. Finally, you can add, commit, and push your solution to github with a single command.

## Updates

### Breaking Changes

+ eatlocal version `0.9.0` only works on the new platform (v2).
+ submitting a bite no longer pushes it to github.
+ bite directories are now names by the bites instead of the number.

## Table of Contents

- [eatlocal](#eatlocal)
  - [Updates](#updates)
    - [Version](#version-080)
    - [Breaking Changes](#breaking-changes)
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
eatlocal download
```

Display bites in the terminal:

```bash
# change the theme with -t <theme name>
eatlocal display
```

Submit bites:

```bash
# use -V, --verbose to print what's happening
eatlocal submit
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

Run `eatlocal init` to configure your PyBites username, PyBites password*, and local git repository.

*Note:  If you signed up for PyBites by authenticating through GitHub or Google, you may need to set a password manually in order to use `eatlocal`.
