import os
from zipfile import ZipFile
import webbrowser
import requests
from io import BytesIO
import subprocess


USER = "russell.helmstedter"
PASSWORD = "not today satan"


def download_bite(bite_number):
    """Download bite .zip from the platform.

    :bite_number: The number of the bite you want to download.
    :returns: None

    """
    zurl = f"https://codechalleng.es/bites/api/downloads/bites/{bite_number}"
    r = requests.get(
        url=zurl,
        auth=(USER, PASSWORD),
        stream=True,
    )
    if r.status_code == 200:
        z = ZipFile(BytesIO(r.content))
        z.extractall(f"./{bite_number}/")
        print(f"bite {bite_number} downloaded and extracted.")
    else:
        print(f"Status code: {r.status_code}")
        print(f"Could not download bite {bite_number}.")


def extract_bite(bite_number):
    """Extracts all the required files into a new directory
    named by the bite number.

    :bite_number: The number of the bite you want to extract.
    :returns: None
    """

    bite = f"pybites_bite{bite_number}.zip"

    try:
        with ZipFile(bite, "r") as zfile:
            zfile.extractall(f"./{bite_number}")

        print(f"Extracted bite {bite_number}")
        os.remove(bite)

    except FileNotFoundError:
        print("No bite found.")


def submit_bite(bite_number):
    """Submits bite by pushing to git hub and opening
    webbrowser to the bit page.

    :bite_number: The number of the bite you want to submit.
    :returns: None

    """
    subprocess.call(
        ["git", "add", "."],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    subprocess.call(
        ["git", "commit", f"-m'submission Bite {bite_number} @ codechalleng.es'"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    subprocess.call(
        ["git", "push"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    # os.system("git add .")
    # os.system(f"git commit -m'submission Bite {bite_number} @ codechalleng.es'")
    # os.system("git push")
    print(f"\nPushed bite {bite_number} to github")

    url = f"https://codechalleng.es/bites/{bite_number}/"
    webbrowser.open(url)
