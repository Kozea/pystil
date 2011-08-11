#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from datetime import datetime, date
from time import mktime
from flask import jsonify
from multicorn.requests import CONTEXT as c
from pystil.corns import Visit
from  pygeoip import GeoIP


def register_data_routes(app):
    """Defines data routes"""
    gip = GeoIP('ip.db')

    @app.route('/visit_by_day.json')
    def visit_by_day():
        today = date.today()
        month_start = datetime(today.year, today.month, 1)
        if today.month == 12:
            year = today.year + 1
            month = 1
        else:
            year = today.year
            month = today.month + 1
        month_end = datetime(year, month, 1)

        visits = [(int(1000 * mktime(
            datetime.strptime(visit['key'], '%Y-%m-%d').timetuple())),
                          visit['count']) for visit in Visit.all
                  .filter((month_start <= c.date) & (c.date < month_end))
                  .map({'day': c.date.str()[:10]})
                  .groupby(c.day, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'label': 'Visits per day',
                        'data': visits, 'color': '#FF00FF'})

    @app.route('/visit_by_time.json')
    def visit_by_time():
        visits = [(int(visit['key']), visit['count'])
                  for visit in Visit.all
                  .map(c.time / 60000)
                  .groupby(c, count=c.len())
                  .execute() if visit['key']]
        return jsonify({'label': 'Time spent on site (in min)', 'data': visits,
                        'color': '#00FF00'})

    @app.route('/visit_by_hour.json')
    def visit_by_hour():
        visits = [(int(visit['key']), visit['count']) for visit in Visit.all
                  .map({'hour': c.date.str()[11:13]})
                  .groupby(c.hour, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'label': 'Visits per hour', 'data': visits})

    @app.route('/visit_by_browser.json')
    def visit_by_browser():
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .groupby(c.browser_name, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'list': visits})

    @app.route('/visit_by_browser_version.json')
    def visit_by_browser_version():
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .groupby(
                      c.browser_name + " " + c.browser_version, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'list': visits})

    @app.route('/visit_by_platform.json')
    def visit_by_platform():
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .groupby(c.platform, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'list': visits})

    @app.route('/visit_by_referrer.json')
    def visit_by_referrer():
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .groupby(c.referrer, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'list': visits})

    @app.route('/visit_by_site.json')
    def visit_by_site():
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .groupby(c.site, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'list': visits})

    @app.route('/visit_by_city.json')
    def visit_by_city():
        ips = Visit.all.map(c.ip) .execute()
        visits = {}
        for ip in ips:
            # TODO Handle class B 172.16.0.0 -> 172.31.255.255
            if (ip == '127.0.0.1'
                or ip.startswith('192.168.')
                or ip.startswith('10.')):
                city = 'Local'
            else:
                location = gip.record_by_addr(ip)
                city = location['city'] if location else 'Unknown'
            visits[city] = visits.get(city, 0) + 1
        visits = [{'label': key,
                   'data': value} for key, value in visits.items()]
        return jsonify({'list': visits})
