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


setup(
        name='pytool',
        version=version(),
        author="Jacob Alheid",
        author_email="jake@about.me",
        description="A Collection of Python Tools",
        long_description=readme(),
        url='http://github.com/shakefu/pytool',
        license='ALv2',
        packages=find_packages(exclude=['test']),
        install_requires=['simplejson >= 3.2.0', 'six'],
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
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities',
            ]
        )
