[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

# eatlocal

Eatlocal helps users solve [Pybites](https://pybitesplatform.com) code challenges locally. This cli tool allows you to download bites from the platform. You can display bite directions directly in the terminal. Once you have solved the bite you can use eatlocal to submit and it offers to open your default browser the corresponding bite page.

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

## Updates

eatlocal 1.0.0+ has been updated to work with version 2.0 of the PyBites platform.

### Breaking Changes

#### Version 1.1.1
+ Moved the local bites database to a new location. It used to be in the directory set by the user, now eatlocal will look for it in `~/.eatlocal`. Run `eatlocal init` to set the new location.

#### Version 1.1.0
+ Uses the bite slug for the name of the directory.

#### Version 1.0.0
+ eatlocal version `1.0.0` only works on the new platform (v2).
+ eatlocal directory no longer has to be a git repository.
+ Submitting a bite no longer pushes it to GitHub.
+ Bite directories are now names by the bites instead of the number.
+ No need to download chrome and chrome driver.
+ No more verbose mode


## Setup

Run `eatlocal init` to configure your PyBites username, PyBites password*, and local where you will solve your bites.

*Note:  If you signed up for PyBites by authenticating through GitHub or Google, you will need to set a password on the platform first.

## Usage

Set up your email, password, and directory where you will solve your bites. It will also create the local bites database, and the cache database:

```bash
eatlocal init
```

Download bites:

```bash
eatlocal download
```

If you want to force a re-download of a given bite use the `--force` flag. This will overwrite the bite directory.

```bash
eatlocal download --force
```

By default, `eatlocal` will cache the bites list and update it every 30 days. If you are not seeing a new bite, then you can clear the cache with the `--clear-cache` flag.

```bash
eatlocal download --clear-cache
```

Display bites in the terminal:

```bash
# change the theme with -t <theme name>
eatlocal display
```

Submit bites:

```bash
eatlocal submit
```

## Installation

There are a few options for install eatlocal.

### Using uv

If you have [uv](https://github.com/astral-sh/uv) installed:

```bash
uv tool install eatlocal
```

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
