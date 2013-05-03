#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat bar data"""
from pystil.context import pystil
from pystil.data.utils import make_serie, on, between
from pystil.aggregates import get_attribute_and_count


def process_data(site, graph, criteria, from_date, to_date, step, stamp, lang):
    table, key, count_col = get_attribute_and_count(criteria)
    rq = (pystil.db
          .query(key.label("key"),
                 count_col.label("count"))
          .filter(on(site, table))
          .filter(between(from_date, to_date, table))
          .group_by(key))
    return make_serie(rq.all(), criteria, lang)
