#!/usr/bin/env python3

from setuptools import setup

setup(
    name='marketo-monkey',
    version='0.1',
    author='Celso Providelo',
    author_email='celso.providelo@canonical.com',
    scripts=['marketo-monkey.py'],
    url='http://pypi.python.org/pypi/marketo-monkey/',
    license='LICENSE',
    description='CLI tool to facilitate Marketo integration',
    install_requires=[
        "python-editor",
        "PyYAML",
        "requests",
    ],
    test_suite='tests',
)
