# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from swift_collate.version import __version__

setup(
    name='swift_collate',
    version=__version__,
    description='A Python API for collating TEI-XML Documents encoded for the Swift Poems Project',
    author='James R. Griffin III',
    author_email='griffinj@lafayette.edu',
    url='https://github.com/LafayetteCollegeLibraries/swift-collate',
    license='GPLv3+',
    packages=find_packages(),
    install_requires=[
        'nltk>=3.2.2',
        'lxml>=3.7.2',
        'collatex==2.0.0rc9'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'])
