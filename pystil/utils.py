# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.


"""Utility functions to help processing data"""
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
from pystil.context import pystil
from pystil.db import Visit
from sqlalchemy.sql import literal, func
import re

IPV4RE = re.compile(r"(\d{1,3}(\.|$)){4}")
BROWSER_VERSION_NUMBERS = {
    'opera': 1,
    'safari': 1,
    'chrome': 1}

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


def on(host, table=Visit.__table__):
    """Generate a filter on a host """
    if host == 'all':
        return literal(True)
    return table.c.host.like('%' + host)


def between(from_date, to_date, table=Visit.__table__):
    """Generate a filter between 2 dates"""
    return ((from_date <= table.c.date) &
            (table.c.date < to_date + timedelta(1)))


def visit_to_table_line(visit):
    html = '<tr data-visit-uuid="%s">' % visit.uuid
    for key in [
            'date', 'site', 'ip', 'country',
            'city', 'page', 'pretty_referrer']:
        html += '<td>'
        val = getattr(visit, key)
        if val:
            if key == 'date':
                val = val.strftime('%Y-%m-%d %H:%M:%S')
            html += val
        html += '</td>'
    html += '</tr>'
    return html


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


def parse_ua(user_agent):
    """Parse the user agent to return the platform, browser and version"""
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
