#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""
pystil - An elegant site web traffic analyzer
"""

from setuptools import setup, find_packages

# Use a time-based version number with ridiculous precision as pip in tox
# does not reinstall the same version.
import datetime
VERSION = "git-" + datetime.datetime.now().isoformat()


options = dict(
    name="pystil",
    version=VERSION,
    description="An elegant site web traffic analyzer",
    long_description=__doc__,
    author="Florian Mounier - Kozea",
    author_email="florian.mounier@kozea.fr",
    license="BSD",
    platforms="Any",
    packages=find_packages(),
    install_requires=['tornado', 'pygal', 'sqlalchemy'],
    package_data={'pystil': [
        'templates/*.html',
        'templates/js/*',
        'static/*.gif',
        'static/js/*',
        'static/stylesheets/*',
    ]},
    classifiers=[
        "Development Status :: WIP",
        "Intended Audience :: Public",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Linux",
        "Programming Language :: Python :: 3.3"])

setup(**options)
