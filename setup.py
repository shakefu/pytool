import multiprocessing, logging # Fix atexit bug
from setuptools import setup, find_packages

import pytool

def readme():
    try:
        return open('README.rst').read()
    except:
        pass
    return ''

setup(
        name='pytool',
        version=pytool.__version__,
        author="Jacob Alheid",
        author_email="jake@about.me",
        description="A Collection of Python Tools",
        long_description=readme(),
        url='http://github.com/shakefu/pytool',
        packages=find_packages(exclude=['test']),
        test_suite='nose.collector',
        tests_require=[
            'nose',
            'mock',
            ],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities',
            ]
        )

