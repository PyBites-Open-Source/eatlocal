import os

from dotenv import load_dotenv

from .cli import get_args
from .eatlocal import extract_bite, submit_bite, download_bite

load_dotenv()

USERNAME = os.environ["PYBITES_USERNAME"]
PASSWORD = os.environ["PYBITES_PASSWORD"]


def main():
    args = get_args()
    if args.extract:
        extract_bite(args.extract)
    elif args.submit:
        submit_bite(args.submit, USERNAME, PASSWORD)
    elif args.download:
        download_bite(args.download, USERNAME, PASSWORD)


if __name__ == "__main__":
    main()
