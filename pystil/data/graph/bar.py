#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat bar data"""

from pystil.db import db, Visit, count
from pystil.data.utils import make_serie, on, between


def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    rq = (db.session
          .query(getattr(Visit, criteria).label("key"),
                 count(1).label("count"))
          .filter(on(site))
          .filter(between(from_date, to_date))
          .filter(getattr(Visit, criteria) != None)
          .group_by(getattr(Visit, criteria)))
    return make_serie(rq.all(), criteria)
