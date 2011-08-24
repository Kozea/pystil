#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""This module process the data to display various graphs"""

from datetime import datetime, date
from time import mktime
from multicorn.requests import CONTEXT as c
from urlparse import urlparse, parse_qs
from pystil.corns import Visit

import re

IPV4RE = re.compile(r"(\d{1,3}(\.|$)){4}")
BROWSER_VERSION_NUMBERS = {
    'opera': 1,
    'safari': 1,
    'chrome': 1}


def label(string):
    """return the label for a criteria"""
    return {
        'new': 'New visits',
        'unique': 'Visits',
        'all': 'Page hits',
        'time': 'Time spent on site',
        'hour': 'Visits per hour'
    }[string]


def str_to_time(date):
    return int(1000 * mktime(datetime.strptime(date, '%Y-%m-%d').timetuple()))


def date_to_time(date):
    return int(1000 * mktime(date.timetuple()))


def time_to_date(time):
    return datetime.fromtimestamp(time / 1000)


def on(host):
    return c.host == host if host != 'all' else True


def between(from_date, to_date):
    return ((time_to_date(from_date) <= c.date) &
            (c.date < time_to_date(to_date)))


def top(dic, size=10):
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


def make_serie(rq, criteria, is_time=False):
    """Create a serie for Flot from request"""
    return {'label': label(criteria),
            'data': [(str_to_time(visit['key']) if is_time
                      else visit['key'],
                      visit['count'])
                     for visit in rq.execute()]}


def base_request(site, from_date, to_date):
    """Common request start"""
    return (Visit.all
            .filter(on(site))
            .filter(between(from_date, to_date)))


# TODO Refactor this
def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    """Return data to be exploited by Flot"""
    rq = base_request(site, from_date, to_date)

    if graph == 'pie':
        if criteria == 'browser_version':
            visits = (rq
                      .filter((c.browser_name != None) &
                              (c.browser_version != None))
                      .map({'label': c.browser_name + ' ' + c.browser_version,
                            'data': 1})
                      .execute())
            version_visits = {}
            for visit in visits:
                label, data = visit['label'], visit['data']
                browser = label.split(' ')[0]
                if '.' in label:
                    label = '.'.join(
                        label.split('.')
                        [:BROWSER_VERSION_NUMBERS.get(browser, 2)])
                if label in version_visits:
                    version_visits[label] += data
                else:
                    version_visits[label] = data
                    visits = [
                        {'label': key, 'data': value}
                        for key, value in top(version_visits)]
            return {'list': visits}

        visits = (rq.filter(getattr(c, criteria) != None)
                  .groupby(getattr(c, criteria), count=c.len())
                  .sort(-c.count)[:10]
                  .execute())

        if criteria == 'referrer':
            results = {}
            for referrer in visits:
                host = urlparse(referrer['key']).netloc.split(':')[0]
                host = host if host else referrer['key']
                results[host] = results.get(host, 0) + referrer['count']
            results = [{'label': key,
                        'data': value} for key, value in top(results)]
            return {'list': results}
        return transform_for_pie(visits, site)

    elif graph == 'line':
        if criteria == 'new':
            rq = rq.filter(c.last_visit == None)
        if criteria == 'unique':
            rq = (rq
                  .map({'day': c.date.str()[:10], 'uuid': c.uuid})
                  .groupby({'day': c.day, 'uuid': c.uuid})
                  .map({'day': c.key.day, 'uuid': c.key.uuid}))
        else:
            rq = rq.map({'day': c.date.str()[:10]})
        rq = rq.groupby(c.day, count=c.len()).sort(c.key)

        return make_serie(rq, criteria, True)

    elif graph == 'map':
        visits = list(rq
                      .filter(c.country_code != None)
                      .groupby(c.country + "$" + c.country_code,
                               count=c.len())
                      .execute())
        return {'list': visits,
                        'max': max(
                            [visit['count'] for visit in visits] + [0])}
    elif graph == 'bar':
        if criteria == 'time':
            rq = (rq.filter(c.time != None)
                      .map(c.time / 60000)
                      .groupby(c, count=c.len()))
            return make_serie(rq, criteria)

        if criteria == 'hour':
            rq = (rq.filter(c.date != None)
                  .map({'hour': c.date.str()[11:13]})  # TODO use date funct
                  .groupby(c.hour, count=c.len()))
            return make_serie(rq, criteria)

    elif graph == 'last':
        visits = [dict(visit) for visit in Visit.all
                      .filter(on(site))
                      .filter(c.date > datetime.fromtimestamp(
                          stamp / 1000) if stamp else True)
                      .sort(-c.date)[:10]
                      .execute()]
        visits.reverse()
        for visit in visits:
            visit['date'] = visit['date'].strftime('%Y-%m-%d %H:%M:%S')
            if visit['last_visit']:
                visit['last_visit'] = date_to_time(visit['last_visit'])
            if visit['lat']:
                visit['lat'] = float(visit['lat'])
            if visit['lng']:
                visit['lng'] = float(visit['lng'])
            url = visit['referrer']
            if url:
                up = urlparse(url)
                netloc = up.netloc
                query = up.query
                search = parse_qs(query).get(
                    'q', parse_qs(query).get(
                        'p', parse_qs(query).get(
                            'rdata', None)))
                if search:
                    # TODO Yahoo variable encoding
                    visit['referrer'] = "Organic: %s %s" % (
                        netloc, search[0].decode('utf-8'))

        return {'list': visits, 'stamp': date_to_time(datetime.today())}
