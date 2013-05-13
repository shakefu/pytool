import multiprocessing, logging # Fix atexit bug
from setuptools import setup, find_packages


__version__ = '0.0.0-dev'  # Fake version for pyflakes
exec("c=__import__('compiler');a='__version__';l=[];g=lambda:[n.expr.value for"
        " n in l for o in n.nodes if o.name==a].pop();c.walk(c.parseFile('%s/_"
        "_init__.py'),type('v',(object,),{'visitAssign':lambda s,n:l.append(n)"
        "})());exec(a+'=g()');"%'pytool')


def readme():
    try:
        return open('README.rst').read()
    except:
        pass
    return ''

setup(
        name='pytool',
        version=__version__,
        author="Jacob Alheid",
        author_email="jake@about.me",
        description="A Collection of Python Tools",
        long_description=readme(),
        url='http://github.com/shakefu/pytool',
        packages=find_packages(exclude=['test']),
        install_requires=['simplejson >= 3.2.0'],
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

