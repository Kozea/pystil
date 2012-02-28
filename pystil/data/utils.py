#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Utility functions to help processing data"""
from flask import current_app
from datetime import datetime, timedelta
from urlparse import urlparse, parse_qs
from pystil import db as models
from pystil.db import Visit, fields
from datetime import date, time
from calendar import timegm
from decimal import Decimal
from sqlalchemy.sql import literal, func
import re
import json

IPV4RE = re.compile(r"(\d{1,3}(\.|$)){4}")
BROWSER_VERSION_NUMBERS = {
    'opera': 1,
    'safari': 1,
    'chrome': 1}


class PystilEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, timedelta):
            return obj.seconds
        if isinstance(obj, time):
            return obj.strftime("%H:%M:%S")
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, str):
            return obj
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def labelize(string, lang):
    """return the label for a criteria"""
    if lang == 'fr':
        return {
            'new': 'Nouvelles visites',
            'unique': 'Visites',
            'all': 'Pages vues',
            'spent_time': u'Temps passé sur de site',
            'hour': 'Visites par heure'
        }[string]

    return {
        'new': 'New visits',
        'unique': 'Visits',
        'all': 'Page hits',
        'spent_time': 'Time spent on site',
        'hour': 'Visits per hour'
    }[string]


def date_to_time(date):
    """Convert a python date to js stamp"""
    return int(1000 * timegm(date.timetuple()))


def time_to_date(time):
    """Convert a js stamp to python date"""
    return datetime.fromtimestamp(time / 1000)


def on(host, table=Visit.__table__):
    """Generate a filter on a host """
    if host == 'all':
        return literal(True)
    return table.c.host.like('%' + host)


def between(from_date, to_date, table=Visit.__table__):
    """Generate a filter between 2 dates"""
    return ((time_to_date(from_date) <= table.c.date) &
            (table.c.date < time_to_date(to_date) + timedelta(1)))


def transform_for_pie(results, site, from_date, to_date, lang,
                      reparse_referrer=False):
    """Transform result for pie display"""
    visits = [{'label': (parse_referrer(visit.key, host_only=True,
                                        second_pass=True)
                         if reparse_referrer else visit.key),
               'data': visit.count}
              for visit in results]
    all_visits = (Visit.query
                  .filter(on(site))
                  .filter(between(from_date, to_date))
                  .count())
    other = all_visits - sum(visit['data'] for visit in visits)
    if other:
        visits = visits + [{'label': 'Other', 'data': other}]
    return {'list': visits}


def make_time_serie(results, criteria, from_date, to_date, lang):
    """Create a serie with 0 days at 0 for Flot from request"""
    visits = {date_to_time(visit.key): visit.count for visit in results}

    for time in range(from_date, to_date, 1000 * 3600 * 24):
        visits[time] = visits.get(time, 0)
    data = visits.items()
    data.sort()
    return {'label': labelize(criteria, lang),
            'data': data}


def make_serie(results, criteria, lang, is_time=False):
    """Create a serie for Flot from request"""
    return {'label': labelize(criteria, lang),
            'data': [(visit.key, visit.count)
                     for visit in results]}


def parse_referrer(referrer, with_query=False, host_only=False,
                   second_pass=False):
    """Return a pretty format for most search engines"""
    if referrer:
        up = urlparse(referrer)
        netloc = up.netloc
        if not netloc:
            if with_query:
                return u"Local: %s" % up.path
            if second_pass:
                return referrer
            return "Local"

        query = up.query
        parsed = parse_qs(query)
        search = parsed.get('q', parsed.get('p', parsed.get('rdata', None)))
        if search:
            # TODO Yahoo variable encoding
            if with_query:
                return u"Organic: %s %s" % (netloc, try_decode(search[0]))
            return u"Organic: %s" % netloc
        if host_only:
            return netloc
        return referrer
    return "Direct"


def parse_domain(referrer):
    """Return the domain of the given referrer."""
    if referrer:
        up = urlparse(referrer)
        netloc = up.netloc
        return netloc or "Local"
    return "Direct"


def polish_visit(visit):
    """Transform a visit for nicer display"""
    if visit['last_visit']:
        visit['last_visit'] = date_to_time(visit['last_visit'])
    if visit['referrer']:
        visit['referrer'] = parse_referrer(visit['referrer'], True)
    visit['date'] = date_to_time(visit['date'])
    return visit


def visit_to_dict(visit):
    visit_dict = {}
    for key in fields(Visit):
        visit_dict[key] = getattr(visit, key)
    return visit_dict


def get_aggregate(criteria):
    """Returns a tuple in the form (model, count_column).
    Tries to look for an aggregate table suitable for the criteria
    """
    model = getattr(models, 'Agg_by_%s' % criteria, Visit)
    if model == Visit:
        current_app.logger.warn('No aggregates for criteria %s' % criteria)
        count = func.count(1)
    else:
        count = func.sum('fact_count')
    return model, count


def try_decode(astring):
    """Try decoding a string in various encodings, with a fallback to good old
    ascii."""
    for encoding in ('utf8', 'latin'):
        try:
            return astring.decode(encoding)
        except UnicodeDecodeError:
            pass
    return astring.decode('ascii', 'ignore')
