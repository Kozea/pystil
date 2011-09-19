#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat last visits data"""


from datetime import datetime
from pystil.data.utils import on, polish_visit, date_to_time, visit_to_dict
from pystil.db import db, Visit


def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    visits = (Visit.query
              .filter(on(site))
              .filter(Visit.date > (datetime.fromtimestamp(
                  stamp / 1000) if stamp else datetime.min))
              .order_by(Visit.date.desc())
              .limit(10)
              .all())

    visits.reverse()

    for visit in visits:
        polish_visit(visit)

    return {'list': [visit_to_dict(visit) for visit in visits],
            'stamp': date_to_time(datetime.today())}
