import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description="Download, extract, and submit PyBites",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-d",
        "--download",
        help="Download bite",
        dest="download",
    )
    group.add_argument(
        "-e",
        "--extract",
        help="Extract files into appropriate directory",
        dest="extract",
    )

    group.add_argument(
        "-s",
        "--submit",
        help="Submit bite",
        dest="submit",
    )
    return parser.parse_args()
