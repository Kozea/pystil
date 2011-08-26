#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Utility functions to help processing data"""

from datetime import datetime, timedelta
from multicorn.requests import CONTEXT as c
from urlparse import urlparse, parse_qs
from pystil.corns import Visit
from time import mktime
import re

IPV4RE = re.compile(r"(\d{1,3}(\.|$)){4}")
BROWSER_VERSION_NUMBERS = {
    'opera': 1,
    'safari': 1,
    'chrome': 1}


def labelize(string):
    """return the label for a criteria"""
    return {
        'new': 'New visits',
        'unique': 'Visits',
        'all': 'Page hits',
        'spent_time': 'Time spent on site',
        'hour': 'Visits per hour'
    }[string]


def str_to_time(date):
    """Parse a date in db format and return a js stamp"""
    return int(1000 * mktime(datetime.strptime(date, '%Y-%m-%d').timetuple()))


def date_to_time(date):
    """Convert a python date to js stamp"""
    return int(1000 * mktime(date.timetuple()))


def time_to_date(time):
    """Convert a js stamp to python date"""
    return datetime.fromtimestamp(time / 1000)


def on(host):
    """Generate a filter on a host """
    return c.host == host if host != 'all' else True


def between(from_date, to_date):
    """Generate a filter between 2 dates"""
    return ((time_to_date(from_date) <= c.date) &
            (c.date < time_to_date(to_date) + timedelta(1)))


def top(dic, size=10):
    """Get only the size top results and put the rest in other"""
    sorted_ = sorted(
        dic.items(),
        lambda x, y: cmp(x[1], y[1]),
        reverse=True)[:min(size, len(dic))]
    other = sum(dic.values()) - sum(value[1] for value in sorted_)
    if other:
        return sorted_ + [['Other', other]]
    return sorted_


def transform_for_pie(results, site):
    """Transform result for pie display"""
    visits = [{'label': visit['key'],
               'data': visit['count']}
              for visit in results]
    all_visits = (Visit.all
                  .filter(on(site))
                  .len()
                  .execute())
    other = all_visits - sum(value['data'] for value in visits)
    if other:
        visits = visits + [{'label': 'Other', 'data': other}]
    return {'list': visits}


def make_time_serie(results, criteria, from_date, to_date):
    """Create a serie with 0 days at 0 for Flot from request"""
    visits = {str_to_time(visit['key']): visit['count'] for visit in results}

    for time in range(from_date, to_date, 1000 * 3600 * 24):
        visits[time] = visits.get(time, 0)
    data = visits.items()
    data.sort()
    return {'label': labelize(criteria),
            'data': data}


def make_serie(results, criteria, is_time=False):
    """Create a serie for Flot from request"""
    return {'label': labelize(criteria),
            'data': [(visit['key'], visit['count'])
                     for visit in results]}


def base_request(site, from_date, to_date):
    """Common request start"""
    return (Visit.all
            .filter(on(site))
            .filter(between(from_date, to_date)))


def cut_browser_version(label):
    """Cut a browser version string for better stats"""
    browser = label.split(' ')[0]
    if '.' in label:
        label = '.'.join(
            label.split('.')
            [:BROWSER_VERSION_NUMBERS.get(browser, 2)])
    return label


def parse_referrer(referrer, with_query=False, host_only=False):
    """Return a pretty format for most search engines"""
    if referrer:
        up = urlparse(referrer)
        netloc = up.netloc
        if not netloc:
            if with_query:
                return "Local: %s" % up.path
            return "Local"

        query = up.query
        search = parse_qs(query).get(
            'q', parse_qs(query).get(
                'p', parse_qs(query).get(
                    'rdata', None)))
        if search:
            # TODO Yahoo variable encoding
            if with_query:
                return "Organic: %s %s" % (netloc, search[0].decode('utf-8'))
            return "Organic: %s" % netloc
        if host_only:
            return netloc
        return referrer
    return "Direct"


def polish_visit(visit):
    """Transform a visit for nicer display"""
    visit['date'] = visit['date'].strftime('%Y-%m-%d %H:%M:%S')
    if visit['last_visit']:
        visit['last_visit'] = date_to_time(visit['last_visit'])
    if visit['lat']:
        visit['lat'] = float(visit['lat'])
    if visit['lng']:
        visit['lng'] = float(visit['lng'])
    visit['referrer'] = parse_referrer(visit['referrer'], True)
