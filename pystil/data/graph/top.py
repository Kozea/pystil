#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""Treat top data"""


from pystil.context import pystil
from pystil.data.utils import on, between
from pystil.aggregates import get_attribute_and_count
from sqlalchemy import desc


def process_data(site, graph, criteria, from_date, to_date, step, stamp, lang):
    table, criterion, count_col = get_attribute_and_count(criteria)

    return {'list':
            [{'key': key,
             'count': count} for key, count in
            pystil.db
            .query(criterion.label("key"),
                   count_col.label("count"))
            .filter(on(site, table))
            .filter(between(from_date, to_date, table=table))
            .group_by(criterion)
            .order_by(desc(count_col))
            .limit(10)
            .all()]}
