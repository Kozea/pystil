#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat map data"""

from pystil.context import pystil
from pystil.db import count
from pystil.data.utils import on, between
from pystil.aggregates import get_attribute_and_count
import os

# with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'map.svg')) as map_file:
#     MAP = map_file.read()


def process_data(site, graph, criteria, from_date, to_date, step, stamp, lang):
    table, criteria, count_col = get_attribute_and_count('country_code')
    rq = (pystil.db
          .query(table.c.country, table.c.country_code,
                 count(1).label("count"))
          .filter(on(site, table))
          .filter(between(from_date, to_date, table))
          .group_by(table.c.country_code, table.c.country))
    visits = [{'country': visit.country,
               'code': visit.country_code,
               'count': visit.count} for visit in rq.all()]
    return {'list': visits,
                    'max': max(
                        [visit['count'] for visit in visits] + [0])}
