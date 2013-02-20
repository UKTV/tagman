#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "tagman",
    version = "0.2.2",
    author = "ReThought Ltd & UKTV",
    author_email = "code@rethought-solutions.com",
    url = "https://github.com/UKTV/tagman.git",

    packages = find_packages('src'),
    package_dir = {'':'src'},
    license = "BSD",
    keywords = "django, tagging, tagman",
    description = "Curated tagging app for Django",
    classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
