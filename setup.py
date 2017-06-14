#!/usr/bin/env python
#coding:utf-8
from __future__ import unicode_literals
from setuptools import setup, find_packages
import setuptools
import codecs
import sys


if sys.version_info[0:2] < (3, 6):
    raise RuntimeError('Requires Python 3.6')


INSTALL_REQUIRES = [
        'pyramid >= 1.8.3',
        'pyramid-chameleon >= 0.3',
        'pymongo >= 3.4.0',
        ]
TESTS_REQUIRE = []


setup(
    name="oai-pmh",
    version="0.1",
    description="OAI-PMH Repository",
    long_description=codecs.open('README.rst', mode='r', encoding='utf-8').read() + '\n\n' +
                     codecs.open('HISTORY.rst', mode='r', encoding='utf-8').read(),
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    maintainer="Gustavo Fonseca",
    maintainer_email="gustavo.fonseca@scielo.org",
    license="BSD License",
    url="http://github.com/scieloorg/oai-pmh",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
    ],
    tests_require=TESTS_REQUIRE,
    test_suite='tests',
    install_requires=INSTALL_REQUIRES,
    entry_points={
    },
)

