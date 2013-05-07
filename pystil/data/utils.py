#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Utility functions to help processing data"""
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from pystil.context import pystil
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


def titlize(string, lang):
    """return the label for a criteria"""
    if lang == 'fr':
        return {
            'all': 'Statistiques par jour',
            'host': 'Top sites',
            'page': 'Pages les plus vues',
            'hash': 'Hashs les plus vus',
            'referrer_domain': 'Top référeurs',
            'hour': 'Visites par heure',
            'browser_name': 'Top navigateurs',
            'browser_name_version': 'Top version de navigateur',
            'size': "Top tailles d'écran",
            'platform': 'Top plateforme',
            'country': 'Top pays',
            'day': 'Top jours',
            'ip': 'Top adresses IP',
        }[string]

    return {
        'all': 'Stats by day',
        'host': 'Top sites',
        'page': 'Most viewed pages',
        'hash': 'Most viewed hashes',
        'referrer_domain': 'Best referrers',
        'hour': 'Visits per hour',
        'browser_name': 'Top browsers',
        'browser_name_version': 'Top browser versions',
        'size': 'Top screen sizes',
        'platform': 'Top platforms',
        'country': 'Top countries',
        'day': 'Top days',
        'ip': 'Top IP addresses'
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


def make_time_serie(results, criteria, from_date, to_date, lang):
    """Create a serie with 0 days at 0 for Flot from request"""
    visits = {date_to_time(visit.key): visit.count for visit in results}
    day_in_ms = 1000 * 3600 * 24
    for time in range(from_date, to_date + day_in_ms, day_in_ms):
        visits[time] = visits.get(time, 0)
    data = list(visits.items())
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
    model = getattr(pystil.db, 'Agg_by_%s' % criteria, Visit)
    if model == Visit:
        pystil.log.warn('No aggregates for criteria %s' % criteria)
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


# Stripped down user agent parsing from werkzeug
PLATFORMS = [(b, re.compile(a, re.I)) for a, b in (
    ('iphone|ios', 'iphone'),
    (r'darwin|mac|os\s*x', 'macos'),
    ('win', 'windows'),
    (r'android', 'android'),
    (r'x11|lin(\b|ux)?', 'linux'),
    ('(sun|i86)os', 'solaris'),
    (r'nintendo\s+wii', 'wii'),
    ('irix', 'irix'),
    ('hp-?ux', 'hpux'),
    ('aix', 'aix'),
    ('sco|unix_sv', 'sco'),
    ('bsd', 'bsd'),
    ('amiga', 'amiga')
)]

BROWSERS = [(
    b, re.compile(r'(?:%s)[/\sa-z(]*(\d+[.\da-z]+)?(?i)' % a)
) for a, b in (
    ('googlebot', 'google'),
    ('msnbot', 'msn'),
    ('yahoo', 'yahoo'),
    ('ask jeeves', 'ask'),
    (r'aol|america\s+online\s+browser', 'aol'),
    ('opera', 'opera'),
    ('chrome', 'chrome'),
    ('firefox|firebird|phoenix|iceweasel', 'firefox'),
    ('galeon', 'galeon'),
    ('safari', 'safari'),
    ('webkit', 'webkit'),
    ('camino', 'camino'),
    ('konqueror', 'konqueror'),
    ('k-meleon', 'kmeleon'),
    ('netscape', 'netscape'),
    (r'msie|microsoft\s+internet\s+explorer', 'msie'),
    ('lynx', 'lynx'),
    ('links', 'links'),
    ('seamonkey|mozilla', 'seamonkey')
)]


def parse_ua(user_agent):
    for platform, regex in PLATFORMS:
        match = regex.search(user_agent)
        if match is not None:
            break
    else:
        platform = None
    for browser, regex in BROWSERS:
        match = regex.search(user_agent)
        if match is not None:
            version = match.group(1)
            break
    else:
        browser = version = None
    return platform, browser, version
