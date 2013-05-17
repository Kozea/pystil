#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""
pystil - An elegant site web traffic analyzer
"""

from setuptools import find_packages, setup

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
    scripts=["pystil2.py"],
    package_data={
        'pystil': ['static/*.js',
                   'static/*.gif',
                   'static/*.png',
                   'static/sylesheets/*',
                   'static/js/*',
                   'static/img/*',
                   'static/font/*',
                   'templates/site/*',
                   'templates/*.html']
    },
    install_requires=['tornado', 'pygal', 'sqlalchemy', 'psycopg2'],
    classifiers=[
        "Development Status :: WIP",
        "Intended Audience :: Public",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Linux",
        "Programming Language :: Python :: 3.3"])

setup(**options)
