#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat line data"""

from pystil.context import pystil
from pystil.data.utils import make_time_serie, on, between
from pystil.db import count, Visit, distinct


def process_data(site, graph, criteria, from_date, to_date, step, stamp, lang):
    rq = (pystil.db
          .query(Visit.day.label("key"),
                 count(distinct(Visit.uuid)).label("count")
                 if criteria == 'unique' else count(1).label("count"))
          .filter(on(site))
          .filter(between(from_date, to_date)))

    if criteria == 'new':
        rq = rq.filter(Visit.last_visit == None)

    results = rq.group_by(Visit.day).order_by(Visit.day).all()
    return make_time_serie(results, criteria, from_date, to_date, lang)
