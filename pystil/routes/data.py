#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.


from datetime import datetime, date
from flask import request, current_app
from functools import wraps
from pystil.data.utils import PystilEncoder
import json


def jsonp(f):
    """Wraps JSONified output for JSONP"""

    """Require user authorization"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + f(*args, **kwargs) + ')'
            return current_app.response_class(
                content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function


def register_data_routes(app, route):
    """Defines data routes"""
    from pystil.db import Visit, fields
    from pystil.data import process_data
    from pystil.data.utils import date_to_time

    url_base = '/<string:site>/<any%r:graph>_by_<any%r:criteria>_in_<lang>' % (
        ('pie', 'bar', 'line', 'table', 'map', 'last'),
        tuple(fields(Visit)) + (
            'all', 'unique', 'new'))
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
    @jsonp
    def data(site, graph, criteria, lang,
             from_date=None, to_date=None, step='day', stamp=None):
        today = date.today()
        month_start = datetime(today.year, today.month, 1)
        from_date = from_date or date_to_time(month_start)
        to_date = to_date or date_to_time(today)
        return json.dumps(process_data(
            site, graph, criteria, from_date, to_date, step, stamp, lang),
                       cls=PystilEncoder)
