#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat map data"""

from pystil.db import db, count
from pystil.data.utils import on, between
from pystil.aggregates import get_attribute_and_count


def process_data(site, graph, criteria, from_date, to_date, step, stamp, lang):
    table, criteria, count_col = get_attribute_and_count('country_code')
    rq = (db.session
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
