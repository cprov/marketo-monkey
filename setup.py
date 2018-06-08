#!/usr/bin/env python3

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='marketo-monkey',
    version='0.1',
    author='Celso Providelo',
    author_email='celso.providelo@canonical.com',
    url="https://github.com/cprov/marketo-monkey",
    license='LICENSE',
    description='CLI tool to facilitate Marketo integration',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        "python-editor",
        "PyYAML",
        "requests",
    ],
    test_suite='tests',
)
