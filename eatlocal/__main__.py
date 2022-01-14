from .eatlocal import extract_bite, submit_bite, download_bite
from .cli import get_args
import os

USERNAME = os.environ.get("PYBITES_USERNAME")
PASSWORD = os.environ.get("PYBITES_PASSWORD")


def main():
    args = get_args()
    if args.extract:
        extract_bite(args.extract)
    elif args.submit:
        submit_bite(args.submit)
    elif args.download:
        download_bite(args.download, USERNAME, PASSWORD)


if __name__ == "__main__":
    main()
