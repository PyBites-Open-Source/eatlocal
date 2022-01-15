import setuptools

setuptools.setup(
    name="eatlocal",
    version="0.4",
    author="Russell Helmstedter",
    author_email="rhelmstedter@gmail.com",
    description="Allows the user to extract and submit pybites",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["eatlocal = eatlocal.__main__:main"]},
    install_requires=[
        'selenium==4.1.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Unix/Linux",
    ],
)
