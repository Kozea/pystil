#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat bar data"""


from multicorn.requests import CONTEXT as c
from pystil.data.utils import base_request, make_serie


def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    rq = base_request(site, from_date, to_date)
    rq = (rq.filter(getattr(c, criteria) != None)
          .groupby(getattr(c, criteria), count=c.len()))
    return make_serie(rq.execute(), criteria)
