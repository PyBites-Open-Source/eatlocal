from pathlib import Path

from dotenv import dotenv_values
from rich.console import Console

console = Console()

def load_config(env_path: Path):
    config = {"PYBITES_USERNAME": "", "PYBITES_PASSWORD": "", "PYBITES_REPO": ""}
    if not env_path.exists():
        console.print(
            "[red]:warning: Could not find or read .eatlocal/.env in your home directory."
        )
        console.print("[yellow]Please run [underline]eatlocal init[/underline] first.")
        return {"PYBITES_USERNAME": "", "PYBITES_PASSWORD": "", "PYBITES_REPO": ""}

    config.update(dotenv_values(dotenv_path=env_path))
    return config


EATLOCAL_HOME = Path().home() / ".eatlocal"
config = load_config(EATLOCAL_HOME / ".env")

BITE_URL = "https://codechalleng.es/bites/api/eatlocal/{bite_number}"
LOGIN_URL = "https://codechalleng.es/login"
SUBMIT_URL = "https://codechalleng.es/bites/{bite_number}"
BITE_ZIPFILE = "pybites_bite{bite_number}.zip"

REPO_WARNING = "[yellow]It seems like you have not set the $PYBITES_REPO environment variable.\nPlease set it, or provide a destination path using the -R flag.[/yellow]"
