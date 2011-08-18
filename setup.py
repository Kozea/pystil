#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
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
    install_requires=['pygeoip', 'Multicorn', "flask", "CSStyle", 'pika'],
    package_data={'pystil': [
        'templates/*.jinja2',
        'templates/css/*',
        'templates/js/*',
        'static/*.gif',
        'static/js/*',
        'static/css/*',
    ]},
    classifiers=[
        "Development Status :: WIP",
        "Intended Audience :: Public",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Linux",
        "Programming Language :: Python :: 2.7"])

setup(**options)
