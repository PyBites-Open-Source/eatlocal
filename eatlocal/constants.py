from pathlib import Path

EATLOCAL_HOME = Path().home() / ".eatlocal"
BITE_URL = "https://codechalleng.es/bites/api/eatlocal/{bite_number}"
LOGIN_URL = "https://codechalleng.es/login"
SUBMIT_URL = "https://codechalleng.es/bites/{bite_number}"
BITE_ZIPFILE = "pybites_bite{bite_number}.zip"
