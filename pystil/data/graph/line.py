#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat line data"""


from multicorn.requests import CONTEXT as c
from pystil.data.utils import make_time_serie, base_request


def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    rq = base_request(site, from_date, to_date)
    if criteria == 'new':
        rq = rq.filter(c.last_visit == None)
    if criteria == 'unique':
        rq = (rq
              .groupby({'day': c.day, 'uuid': c.uuid})
              .map({'day': c.key.day, 'uuid': c.key.uuid}))
    results = rq.groupby(c.day, count=c.len()).sort(c.key).execute()
    return make_time_serie(results, criteria, from_date, to_date)
