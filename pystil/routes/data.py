#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from datetime import datetime, date
from time import mktime
from flask import jsonify
from multicorn.requests import CONTEXT as c
from urlparse import urlparse
import re

IPV4RE = re.compile(r"(\d{1,3}(\.|$)){4}")
BROWSER_VERSION_NUMBERS = {
    'opera': 1,
    'safari': 1,
    'chrome': 1}


def register_data_routes(app, route):
    """Defines data routes"""
    from pystil.corns import Visit
    log = app.logger

    def str_to_time(date):
        return int(1000 * mktime(
            datetime.strptime(date, '%Y-%m-%d').timetuple()))

    def date_to_time(date):
        return int(1000 * mktime(date.timetuple()))

    def on(host):
        return c.host == host if host != '*' else True

    def top(dic, size=10):
        sorted_ = sorted(
            dic.items(),
            lambda x, y: cmp(x[1], y[1]),
            reverse=True)[:min(size, len(dic))]
        other = sum(dic.values()) - sum(value[1] for value in sorted_)
        if other:
            return sorted_ + [['Other', other]]
        return sorted_

    def mc_top(visits, site):
        visits = list(visits)
        all_visits = (Visit.all
                      .filter(on(site))
                      .len()
                      .execute())
        other = all_visits - sum(value['data'] for value in visits)
        if other:
            return visits + [{'label': 'Other', 'data': other}]
        return visits

    @route('/<site>/line_by_day.json')
    def line_by_day(site):
        today = date.today()
        month_start = datetime(today.year, today.month, 1)
        if today.month == 12:
            year = today.year + 1
            month = 1
        else:
            year = today.year
            month = today.month + 1
        month_end = datetime(year, month, 1)

        page_hits = [(str_to_time(visit['key']),
                      visit['count']) for visit in Visit.all
                  .filter(on(site))
                  .filter((month_start <= c.date) & (c.date < month_end))
                  .map({'day': c.date.str()[:10]})
                  .groupby(c.day, count=c.len())
                  .sort(c.key)
                  .execute()]

        new_visits = [(str_to_time(visit['key']),
                          visit['count']) for visit in Visit.all
                  .filter(on(site))
                  .filter((month_start <= c.date) & (c.date < month_end))
                  .filter(c.last_visit == None)
                  .map({'day': c.date.str()[:10]})
                  .groupby(c.day, count=c.len())
                  .sort(c.key)
                  .execute()]

        # TODO: Make it work in MC
        # visits = [(int(1000 * mktime(
        #     datetime.strptime(visit['key'], '%Y-%m-%d').timetuple())),
        #                   visit['count']) for visit in Visit.all
        #           .filter(on(site))
        #           .filter((month_start <= c.date) & (c.date < month_end))
        #           .map({'day': c.date.str()[:10], 'uuid': c.uuid})
        #           .groupby({'day': c.day, 'uuid: c.uuid}, count=c.len())
        #           .map({'day': c.key.day, 'val': c.count})
        #           .groupby(c.day, count=c.len())
        #           .sort(c.key)
        #           .execute()]
        return jsonify({'series': [
            {'label': 'Page hits',
             'data': page_hits},
            # {'label': 'Visits',
            #  'data': visits},
            {'label': 'New visits',
             'data': new_visits}]})

    @route('/<site>/bar_by_time.json')
    def bar_by_time(site):
        visits = [(visit['key'], visit['count'])
                  for visit in Visit.all
                  .filter(on(site) & (c.time != None))
                  .map(c.time / 60000)
                  .groupby(c, count=c.len())
                  .execute()]
        return jsonify({'label': 'Time spent on site (in min)',
                        'data': visits,
                        'color': '#00FF00'})

    @route('/<site>/bar_by_hour.json')
    def bar_by_hour(site):
        visits = [(int(visit['key']), visit['count']) for visit in Visit.all
                  .filter(on(site))
                  .map({'hour': c.date.str()[11:13]})
                  .groupby(c.hour, count=c.len())
                  .execute()]
        return jsonify({'label': 'Visits per hour', 'data': visits})

    @route('/<site>/pie_by_<any%r:criteria>.json' % (tuple(Visit.properties),))
    def pie_by_criteria(site, criteria):
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .filter(on(site))
                  .filter(getattr(c, criteria) != None)
                  .groupby(getattr(c, criteria), count=c.len())
                  .sort(-c.count)[:10]
                  .execute()]
        return jsonify({'list': mc_top(visits, site)})

    @route('/<site>/pie_by_simple_referrer.json')
    def pie_by_simple_referrer(site):
        full_referrers = (Visit.all
                  .filter(on(site))
                  .filter(c.referrer != None)
                  .groupby(c.referrer, count=c.len())
                  .map({'label': c.key, 'data': c.count})
                  .sort(-c.data)[:10]
                  .execute())
        visits = {}
        for referrer in full_referrers:
            host = urlparse(referrer['label']).netloc.split(':')[0]
            host = host if host else referrer['label']
            visits[host] = visits.get(host, 0) + referrer['data']
        visits = [{'label': key,
                   'data': value} for key, value in top(visits)]
        return jsonify({'list': visits})

    @route('/<site>/pie_by_browser_with_version.json')
    def pie_by_browser_with_version(site):
        visits = (Visit.all
                  .filter(on(site))
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
                    label.split('.')[:BROWSER_VERSION_NUMBERS.get(browser, 2)])
            if label in version_visits:
                version_visits[label] += data
            else:
                version_visits[label] = data
        visits = [
            {'label': key, 'data': value}
            for key, value in top(version_visits)]

        return jsonify({'list': visits})

    @route('/<site>/map_by_visit.json')
    def map_by_visit(site):
        visits = list(Visit.all
                      .filter(on(site))
                      .filter(c.country_code != None)
                      .groupby(c.country + "$" + c.country_code,
                               count=c.len())
                      .execute())
        return jsonify({'list': visits,
                        'max': max(
                            [visit['count'] for visit in visits] + [0])})

    @route('/<site>/<int:stamp>/last_visits.json')
    def last_visits(site, stamp):
        visits = [dict(visit) for visit in Visit.all
                      .filter(on(site))
                      .filter(c.date > datetime.fromtimestamp(
                          stamp / 1000))
                      .sort(-c.date)[:10]
                      .execute()]
        for visit in visits:
            visit['date'] = date_to_time(visit['date'])
            if visit['last_visit']:
                visit['last_visit'] = date_to_time(visit['last_visit'])
        return jsonify({'list': visits})
