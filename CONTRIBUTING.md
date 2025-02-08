### Contributing Guide

Welcome to the **EatLocal**! We appreciate your interest in contributing. This guide will help you set up the project locally and get started with development.

Follow these steps to set up the **EatLocal** project locally:

---

### 1. **Fork and Clone the Repository**
1. Fork the repository to your GitHub account.
2. [Clone your forked repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) to your local machine. 
3. Set the upstream repository to keep your fork updated:
   ```bash
   git remote add upstream https://github.com/PyBites-Open-Source/eatlocal.git
   git fetch upstream
   ```


### 2. **Set Up Python Environment**
1. Ensure you have **Python 3.12.0** or greater installed. You can download it from the [official Python website](https://www.python.org/downloads/release/python-3120/).
2. Create a virtual environment using `venv` or any other tool you prefer:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```


### 3. **Install `pip`**
1. Ensure you have the latest version of `pip` installed. If not, follow the [official pip installation guide](https://pip.pypa.io/en/stable/installation/).
2. Upgrade `pip` to the latest version:
   ```bash
   python -m pip install --upgrade pip
   ```


### 4. **Install `uv`**
1. Install `uv`, a fast and efficient package installer:
   ```bash
   python -m pip install uv
   ```
   - Alternatively, you can install `uv` using a standalone installer. Check the [official `uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) for more options.

### 5. **Install Pre-commit**
1. Install `pre-commit` so all the [hooks](https://github.com/PyBites-Open-Source/eatlocal/blob/main/.pre-commit-config.yaml) can be automatically be run whenever you commit your changes.
```Python
python -m pip install pre-commit
pre-commit install
```
2. (optional) Run against all the files
```Python
pre-commit run --all-files
```


### 6. **Install Dependencies in Editable Mode**
1. Install the project in **editable mode** using `uv`. This allows you to make changes to the code without reinstalling the package:
   ```bash
   uv pip install --editable .
   ```
   - The `--editable` flag (or `-e`) creates a symbolic link to your project directory, making it ideal for development.


### 7. **Verify the Setup**
1. Check that the package is installed in editable mode:
   ```bash
   pip list
   ```
   You should see your package listed with a path to your project directory.

Now you are all set. We look forward to your contributions. Thank you for contributing to **EatLocal**! 🚀  