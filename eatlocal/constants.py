import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.environ["PYBITES_USERNAME"]
PASSWORD = os.environ["PYBITES_PASSWORD"]
BITE_URL = "https://codechalleng.es/bites/api/eatlocal/{bite_number}"
