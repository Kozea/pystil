#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.


from datetime import datetime, date
from flask import jsonify
from multicorn.requests import CONTEXT as c
from urlparse import urlparse, parse_qs
import re


def register_data_routes(app, route):
    """Defines data routes"""
    from pystil.corns import Visit
    from pystil.data import process_data, date_to_time
    log = app.logger

    url_base = '/<string:site>/<any%r:graph>_by_<any%r:criteria>' % (
        ('pie', 'bar', 'line', 'table', 'map', 'last'),
        tuple(Visit.properties) + (
            'all', 'unique', 'new', 'hour', 'time'))
    url_with_at = '%s_at_<int:stamp>' % url_base
    url_with_from = '%s_from_<int:from_date>' % url_base
    url_with_to = '%s_to_<int:to_date>' % url_with_from
    url_with_step = '%s_step_<any%r:step>' % (url_with_to, (
        'hour', 'day', 'week', 'year'))

    @route('%s.json' % url_base)
    @route('%s.json' % url_with_at)
    @route('%s.json' % url_with_from)
    @route('%s.json' % url_with_to)
    @route('%s.json' % url_with_step)
    def data(site, graph, criteria,
             from_date=None, to_date=None, step='day', stamp=0):
        today = date.today()
        month_start = datetime(today.year, today.month, 1)
        from_date = from_date or date_to_time(month_start)
        to_date = to_date or date_to_time(today)
        return jsonify(process_data(
            site, graph, criteria, from_date, to_date, step, stamp))
