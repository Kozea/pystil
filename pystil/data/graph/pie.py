#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""Treat pie data"""
from pystil.db import db, desc
from pystil.data.utils import on, between, parse_referrer
from pystil.aggregates import get_attribute_and_count


def process_data(site, graph, criteria, from_date, to_date, step, stamp, lang):
    table, criterion, count_col = get_attribute_and_count(criteria)
    restrict = (criterion != None)
    if criteria == 'browser_name_version':
        restrict = ((table.c.browser_name != None) &
                    (table.c.browser_version != None))
    rq = (db.session
          .query(criterion.label("key"),
                 count_col.label("count"))
          .filter(on(site, table))
          .filter(between(from_date, to_date, table=table))
          .filter(restrict)
          .group_by(criterion)
          .order_by(desc(count_col)))
    results = rq.limit(10).all()
    visits = [{'label': (
        parse_referrer(visit.key, host_only=True, second_pass=True)
        if criteria == 'pretty_referrer' else visit.key),
               'data': visit.count}
              for visit in results]
    all_visits = (db.session
                  .query(count_col.label("all"))
                  .filter(on(site, table))
                  .filter(between(from_date, to_date, table=table))
                  .filter(restrict)
                  .first()).all or 0
    other = all_visits - sum(visit['data'] for visit in visits)
    if other:
        visits = visits + [{'label': 'Other', 'data': other}]
    return {'list': visits}
