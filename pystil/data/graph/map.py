#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat map data"""

from pystil.db import db, Visit, count
from pystil.data.utils import on, between


def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    rq = (db.session
          .query(Visit.country, Visit.country_code,
                 count(1).label("count"))
          .filter(on(site))
          .filter(between(from_date, to_date))
          .filter(Visit.country != None)
          .filter(Visit.country_code != None)
          .group_by(Visit.country_code, Visit.country))
    visits = [{'country': visit.country,
               'code': visit.country_code,
               'count': visit.count} for visit in rq.all()]
    return {'list': visits,
                    'max': max(
                        [visit['count'] for visit in visits] + [0])}
