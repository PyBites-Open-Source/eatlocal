import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.environ.get("PYBITES_USERNAME", None)
PASSWORD = os.environ.get("PYBITES_PASSWORD", None)
BITE_URL = "https://codechalleng.es/bites/api/eatlocal/{bite_number}"
