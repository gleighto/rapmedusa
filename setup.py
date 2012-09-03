#!/usr/bin/env python
import os

from rapmedusa import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
long_description = f.read()
f.close()

setup(
    name='rapmedusa',
    version=__version__,
    description='Python implementation of MapReduce querying for Redis',
    long_description=long_description,
    url='http://github.com/gleighto/rapmedusa',
    download_url=('http://cloud.github.com/downloads/gleighto/'
                  'rapmedusa/rapmedusa-%s.tar.gz' % __version__),
    author='Greg Leighton',
    author_email='grleighton@gmail.com',
    maintainer='Greg Leighton',
    maintainer_email='grleighton@gmail.com',
    keywords=['Redis', 'key-value store', 'MapReduce'],
    license='MIT',
    packages=['rapmedusa'],
    test_suite='tests.all_tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7' 
        ],
    install_requires=[
        "redis >= 2.0"
    ],
)
