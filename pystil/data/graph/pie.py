#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""Treat pie data"""


from pystil.db import Visit, db, count, desc
from pystil.data.utils import transform_for_pie, on, between


def process_data(site, graph, criterion, from_date, to_date, step, stamp):
    criteria = getattr(Visit, criterion)
    restrict = criteria != None
    if criterion == 'browser_name_version':
        restrict = ((Visit.browser_name != None) &
                    (Visit.browser_version != None))

    rq = (db.session
          .query(criteria.label("key"),
                 count("*").label("count"))
          .filter(on(site))
          .filter(between(from_date, to_date))
          .filter(restrict)
          .group_by(criteria)
          .order_by(desc("count")))
    return transform_for_pie(rq.limit(10).all(), site,
                             criterion == 'pretty_referrer')
