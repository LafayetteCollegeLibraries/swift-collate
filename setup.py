# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='swift_collate',
    version='0.0.1',
    description='A Python API for collating TEI-XML Documents encoded for the Swift Poems Project',
    author='James R. Griffin III',
    author_email='griffinj@lafayette.edu',
    url='https://github.com/LafayetteCollegeLibraries/swift-collate',
    license='GPLv3+',
    packages=find_packages(),
    install_requires=[
        'nltk==3.2.2',
        'lxml==3.7.2',
        'collatex==2.0.0rc9',
        'decorator==4.0.11',
        'networkx==1.11',
        'packaging==16.8',
        'prettytable==0.7.2',
        'py==1.4.32',
        'pyparsing==2.1.10',
        'pytest==3.0.6',
        'six==1.10.0'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'])
