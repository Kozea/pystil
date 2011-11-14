#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""Treat pie data"""


from pystil.db import db, desc
from pystil.data.utils import transform_for_pie, on, between
from pystil.aggregates import get_attribute_and_count


def process_data(site, graph, criterion, from_date, to_date, step, stamp):
    table, criteria, count_col  = get_attribute_and_count(criterion)
    restrict = criteria != None
    rq = (db.session
          .query(criteria.label("key"),
                 count_col.label("count"))
          .filter(on(site, table))
          .filter(between(from_date, to_date, table=table))
          .filter(restrict)
          .group_by(criteria)
          .order_by(desc(count_col)))
    return transform_for_pie(rq.limit(10).all(), site, from_date, to_date,
                             criterion == 'pretty_referrer')
