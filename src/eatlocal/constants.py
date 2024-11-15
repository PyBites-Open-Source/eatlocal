from pathlib import Path
from enum import Enum


class ConsoleStyle(Enum):
    SUCCESS = "green"
    SUGGESTION = "yellow"
    WARNING = "red"


BITE_URL = "https://pybitesplatform.com/bites/{bite_slug}/"
EATLOCAL_HOME = Path().home() / ".eatlocal"
CACHE_DB_LOCATION = EATLOCAL_HOME / ".bites_list_cache.sqlite"
LOCAL_BITES_DB = EATLOCAL_HOME / ".local_bites.json"
BITES_API = "https://pybitesplatform.com/api/bites/"
FZF_DEFAULT_OPTS = "--height 13 --layout=reverse --border rounded --margin=2%,5%,10%,2%"
LOGIN_URL = "https://pybitesplatform.com/accounts/auth/login/"
PROFILE_URL = "https://pybitesplatform.com/accounts/profile/"
TIMEOUT_LENGTH = 30000
