import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.environ.get("PYBITES_USERNAME", None)
PASSWORD = os.environ.get("PYBITES_PASSWORD", None)
BITE_REPO = os.environ.get("PYBITES_REPO", None)

BITE_URL = "https://codechalleng.es/bites/api/eatlocal/{bite_number}"
LOGIN_URL = "https://codechalleng.es/login"
SUBMIT_URL = "https://codechalleng.es/bites/{bite_number}"
BITE_ZIPFILE = "pybites_bite{bite_number}.zip"
