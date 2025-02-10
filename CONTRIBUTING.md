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


### 2. **Set Up Python Environment and Install Dependencies**
1. Ensure you have **Python 3.12.0** or greater installed. You can download it from the [official Python website](https://www.python.org/downloads/release/python-3120/).

2. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

3. Sync and install all dependencies:
   ```Python
      uv sync
   ```
      * If you want to prevent having to reinstall the package, you can also install it in editable mode:
      ```Python
      uv pip install --editable .
      ```

### 3. Install Pre-commit Hooks

1. Install pre-commit hooks to ensure code consistency:

```Python
uvx pre-commit install
```

2. *(Optional)* Run the hooks against all files:
```Python
uvx pre-commit run --all-files
```

### 4. Verify the Setup

Check that everything is set up correctly by running the project:

```Python
uv run eatlocal
```

Now you are all set. We look forward to your contributions. Thank you for contributing to **EatLocal**! 🚀  