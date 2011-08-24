#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat map data"""


from multicorn.requests import CONTEXT as c
from pystil.data.utils import base_request


def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    rq = base_request(site, from_date, to_date)
    visits = list(rq
                  .filter(c.country_code != None)
                  .groupby(c.country + "$" + c.country_code,
                           count=c.len())
                  .execute())
    return {'list': visits,
                    'max': max(
                        [visit['count'] for visit in visits] + [0])}
