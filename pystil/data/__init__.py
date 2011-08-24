#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""This module process the data to display various graphs"""

from pystil.data.graph import pie, bar, last, line, map

SWITCH = {
    'bar': bar.process_data,
    'last': last.process_data,
    'line': line.process_data,
    'map': map.process_data,
    'pie': pie.process_data,
}


def process_data(*args):
    """Dispatch graph treatments to return data to Flot"""
    return SWITCH[args[1]](*args)
