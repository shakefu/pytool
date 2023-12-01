from setuptools import setup, find_packages


def readme():
    try:
        return open('README.rst').read()
    except Exception as err:  # noqa
        pass
    return ''


def version():
    try:
        import re
        return re.search("^__version__ = '(.*)'",
                         open('pytool/__init__.py').read(), re.M).group(1)
    except Exception as err:
        raise RuntimeError("Could not get version:\n" + str(err))

TESTS_REQUIRE = [
        'bson',
        'configargparse',
        'coverage',
        'coveralls',
        'mock',
        'pytest',
        ]

setup(
    name='pytool',
    version=version(),
    author="Jacob Alheid",
    author_email="jacob.alheid@gmail.com",
    description="A Collection of Python Tools",
    long_description=readme(),
    url='http://github.com/shakefu/pytool',
    license='ALv2',
    packages=find_packages(exclude=['test']),
    install_requires=['simplejson >= 3.2.0', 'six'],
    tests_require=TESTS_REQUIRE,
    extras_require={ "test": TESTS_REQUIRE},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        ]
    )
