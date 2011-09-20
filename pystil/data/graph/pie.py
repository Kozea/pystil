#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""Treat pie data"""


from pystil.db import Visit, db, count, desc
from pystil.data.utils import (top, transform_for_pie, on, between,
                               cut_browser_version, parse_referrer)


def process_data(site, graph, criterion, from_date, to_date, step, stamp):
    reaggreg = None
    criteria = getattr(Visit, criterion)
    restrict = criteria != None
    if criterion == 'browser_name_version':
        restrict = ((Visit.browser_name != None) &
                    (Visit.browser_version != None))

    if criterion == 'browser_version':
        restrict = ((Visit.browser_name != None) &
                    (Visit.browser_version != None))
        reaggreg = cut_browser_version

    if criterion == 'referrer':
        def host_only_referrer(key):
            return parse_referrer(key, host_only=True)
        reaggreg = host_only_referrer

    rq = (db.session
          .query(criteria.label("key"),
                 count("*").label("count"))
          .filter(on(site))
          .filter(between(from_date, to_date))
          .filter(restrict)
          .group_by(criteria)
          .order_by(desc("count")))

    if reaggreg:
        results = {}
        for result in rq.all():
            reaggreger = reaggreg(result.key)
            results[reaggreger] = results.get(reaggreger, 0) + result.count
        results = [{'label': key,
                    'data': value} for key, value in top(results)]
        return {'list': results}
    return transform_for_pie(rq.limit(10).all(), site)
