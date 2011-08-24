#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat bar data"""


from multicorn.requests import CONTEXT as c
from pystil.data.utils import base_request, make_serie


def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    rq = base_request(site, from_date, to_date)

    if criteria == 'time':
        rq = (rq.filter(c.time != None)
                  .map(c.time / 60000)
                  .groupby(c, count=c.len()))
        return make_serie(rq, criteria)

    if criteria == 'hour':
        rq = (rq.filter(c.date != None)
              .map({'hour': c.date.str()[11:13]})  # TODO use date funct
              .groupby(c.hour, count=c.len()))
        return make_serie(rq, criteria)
