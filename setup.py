import setuptools 

setuptools.setup( 
    name='eatlocal', 
    version='0.2', 
    author='Russell Helmstedter', 
    author_email='rhelmstedter@gmail.com', 
    description='Allows the user to extract and submit pybites', 
    packages=setuptools.find_packages(), 
    entry_points={ 
        'console_scripts': [ 
            'eatlocal = eatlocal.__main__:main' 
        ] 
    }, 
    classifiers=[ 
        'Programming Language :: Python :: 3', 
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Unix/Linux', 
    ], 
)
