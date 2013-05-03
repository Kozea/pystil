#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat last visits data"""

from datetime import datetime
from pystil.data.utils import on, polish_visit, visit_to_dict
from pystil.db import Visit
from pystil.events import get_poll


def process_data(site, graph, criteria, from_date, to_date, step, stamp, lang):
    return {}

    poll = get_poll(site)
    if stamp == None:
        visits = (Visit.query
              .filter(on(site))
              .filter(Visit.date > (datetime.utcfromtimestamp(
                  stamp / 1000) if stamp else datetime.min))
              .order_by(Visit.date.desc())
              .limit(10)
              .all())

        visits.reverse()
        visits = [polish_visit(visit_to_dict(visit)) for visit in visits]
        stamp = len(poll.visits)
    else:
        visits, stamp = poll.get(stamp)

    return {'list': visits, 'stamp': stamp}
