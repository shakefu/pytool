import multiprocessing, logging # Fix atexit bug
from setuptools import setup, find_packages

import pytool


setup(
        name='pytool',
        version=pytool.__version__,
        description="A Collection of Python Tools",
        author="Jacob Alheid",
        author_email="jake@about.me",
        packages=find_packages(exclude=['test']),
        install_requires=[],
        test_suite='nose.collector',
        tests_require=[
            'nose',
            'mock',
            ],
        )

