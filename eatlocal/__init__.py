""" A package to solve PyBites locally"""

import pkg_resources

__version__ = pkg_resources.get_distribution('eatlocal').version

if __name__ == "__main__":
    print(__version__)
