#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat last visits data"""


from datetime import datetime
from multicorn.requests import CONTEXT as c
from pystil.corns import Visit
from pystil.data.utils import on, polish_visit, date_to_time


def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    visits = [dict(visit) for visit in Visit.all
                  .filter(on(site))
                  .filter(c.date > datetime.fromtimestamp(
                      stamp / 1000) if stamp else True)
                  .sort(-c.date)[:10]
                  .execute()]
    visits.reverse()
    for visit in visits:
        polish_visit(visit)

    return {'list': visits, 'stamp': date_to_time(datetime.today())}
